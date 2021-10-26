let navbar = document.querySelector('.navbar');

document.querySelector('#menu-btn').onclick = () =>{
    navbar.classList.toggle('active');
    searchForm.classList.remove('active');
    cart.classList.remove('active');
    loginForm.classList.remove('active');
}

window.onscroll = () =>{
    searchForm.classList.remove('active');
    cart.classList.remove('active');
    loginForm.classList.remove('active');
    navbar.classList.remove('active');
}


let lista = document.querySelectorAll('.lista');
for (let i=0; i<lista.length; i++){
    lista[i].onclick = function(){
        let j = 0;
        while(j < lista.length){
            lista[j++].className = 'lista';
        }
        lista[i].className = 'lista activa';
    }
}
