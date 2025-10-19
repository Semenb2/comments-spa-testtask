let currentSort = "-created_at";
let currentPage = 1;

document.addEventListener("DOMContentLoaded", () => {
    loadComments();
    refreshCaptcha();
});

function loadComments(sort = currentSort, page = currentPage) {
    currentSort = sort;
    currentPage = page;
    fetch(`/api/comments/?sort=${sort}&page=${page}`)
        .then(r => r.json())
        .then(data => {
            renderComments(data.results);
            renderPagination(data);
        });
}

function renderComments(comments) {
    const container = document.getElementById("comments");
    container.innerHTML = "";
    comments.forEach(comment => {
        container.appendChild(renderCommentBlock(comment, 0));
    });
}

function renderCommentBlock(comment, level) {
    const div = document.createElement("div");
    div.className = "comment-block";
    div.style.marginLeft = `${level * 20}px`;

    div.innerHTML = `
        <p><strong>${comment.user.username}</strong> (${comment.user.email})</p>
        <p>${comment.text}</p>
        ${renderAttachments(comment.attachments)}
        <button onclick="showReplyForm(${comment.id})">Ответить</button>
        <div id="reply-form-${comment.id}" class="reply-form" style="display:none;">
            <input type="text" id="reply-username-${comment.id}" placeholder="Ваше имя">
            <input type="email" id="reply-email-${comment.id}" placeholder="Ваш email">
            <textarea id="reply-text-${comment.id}" placeholder="Ваш ответ"></textarea>
            <button onclick="sendReply(${comment.id})">Отправить</button>
        </div>
    `;

    if (comment.replies) {
        comment.replies.forEach(reply => {
            div.appendChild(renderCommentBlock(reply, level + 1));
        });
    }
    return div;
}

function renderAttachments(files) {
    if (!files || files.length === 0) return "";
    return files.map(file => {
        if (file.type === "image") {
            return `<img src="${file.file}" class="thumb" onclick="openLightbox('${file.file}')">`;
        } else {
            return `<a href="${file.file}" target="_blank">TXT файл (${file.size_bytes} байт)</a>`;
        }
    }).join("<br>");
}

async function sendComment() {
    const username = document.getElementById("username").value.trim();
    const email = document.getElementById("email").value.trim();
    const text = document.getElementById("text").value.trim();
    const captcha = document.getElementById("captcha").value.trim();

    if (!username || !email || !text || !captcha) {
        return alert("Имя, Email, текст и CAPTCHA обязательны!");
    }

    const res = await fetch("/api/comments/create/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, email, text, captcha })
    });

    if (!res.ok) {
        const e = await res.json();
        alert(e.error || "Ошибка сервера");
        refreshCaptcha();
        return;
    }

    const comment = await res.json();

    const fileInput = document.getElementById("file");
    if (fileInput.files.length > 0) {
        const form = new FormData();
        form.append("file", fileInput.files[0]);
        await fetch(`/api/comments/${comment.id}/attachments/`, {
            method: "POST",
            body: form
        });
        fileInput.value = "";
    }

    document.getElementById("text").value = "";
    document.getElementById("captcha").value = "";
    refreshCaptcha();
    loadComments();
}

function showReplyForm(id) {
    document.getElementById(`reply-form-${id}`).style.display = "block";
}

function sendReply(id) {
    const username = document.getElementById(`reply-username-${id}`).value.trim();
    const email = document.getElementById(`reply-email-${id}`).value.trim();
    const text = document.getElementById(`reply-text-${id}`).value.trim();

    fetch(`/api/comments/${id}/reply/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, email, text })
    }).then(() => loadComments());
}

function preview() {
    const box = document.getElementById("preview");
    box.innerHTML = document.getElementById("text").value;
}

function refreshCaptcha() {
    document.getElementById("captcha-img").src = "/api/captcha/?t=" + new Date().getTime();
}

function openLightbox(url) {
    document.getElementById("lightbox-img").src = url;
    document.getElementById("lightbox").style.display = "flex";
}
function closeLightbox() {
    document.getElementById("lightbox").style.display = "none";
}

function sortComments(field) {
    if (currentSort === field) field = "-" + field;
    loadComments(field, 1);
}

function renderPagination(data) {
    const div = document.getElementById("pagination");
    div.innerHTML = "";

    if (data.previous) {
        const prev = document.createElement("button");
        prev.textContent = "← Назад";
        prev.onclick = () => loadComments(currentSort, currentPage - 1);
        div.appendChild(prev);
    }

    if (data.next) {
        const next = document.createElement("button");
        next.textContent = "Вперёд →";
        next.onclick = () => loadComments(currentSort, currentPage + 1);
        div.appendChild(next);
    }
}
