const $ = (id) => document.getElementById(id)
const msg = $("msg");

function showMsg(text){
    msg.textContent = text;
    msg.classList.remove("hidden");
}

function hidemsg(){
    msg.textContent = "";
    msg.classList.add("hidden");
}

async function login() {
    hidemsg();
    const email = $("email").value.trim();
    const password = $("password").value; 

    const body = new URLSearchParams();
    body.set("email", email);
    body.set("password", password);

    const res = await fetch("/api/login", {
        method: "POST",
        credentials:"include",
        headers:{"Content-Type":"application/x-www-form-urlencoded"},
        body
    });

    if (!res.ok){
        const t = await res.text();
        try{
            const j = JSON.parse(t);
            showMsg(j.detail || "Login Fallito!");
        }catch{
            showMsg(t || "Login Fallito!");
        }
        return ;
    }

    //Vai alla pagina movimenti
    window.location.href = "/movimenti";

}

$("btnLogin").addEventListener("click", login);

document.getElementById("btnGoRegister").addEventListener("click", () => {
    window.location.href = "/register";
});