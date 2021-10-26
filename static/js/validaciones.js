function mostrarPassword(){
    var obj = document.getElementById("password");
    var ojito=document.getElementById("ojito");
    
    if (obj.type=="password"){
        obj.type = "text";
        ojito.classList.toggle("far fa-eye-slash");
                
    }else{
        obj.type = "password";
        ojito.classList.toggle("far fa-eye");
        
    }    
}

function validar_form_login(){
     
    correoRegistro=document.getElementById("correo").value;
    passwordRegistro=document.getElementById("password").value;
    var expReg= /^[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?$/;

    if ( correoRegistro == "" ){        
        alert(" El campo del correo electrónico no debe estar vacío.");
        //return false;
    }else if ( expReg.test(correoRegistro) == false ){
        alert("No es un correo elctrónico válido.");    
        //return false;
    }else if ( passwordRegistro == "" ){
        alert("El campo Contraseña no debe estar vacío.");
        //return false;
    }else if ( passwordRegistro.length < 8 ){
        alert("El campo Contraseña debe tener mínimo 8 caracteres");
        //return false;
    }

}

function validar_form_registro(){
    
    nombresRegistro=document.getElementById("nombres").value;
    apellidosRegistro=document.getElementById("apellidos").value;
    correoRegistro=document.getElementById("correo").value;
    passwordRegistro=document.getElementById("password").value;
    var expReg= /^[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?$/;
    
    if ( nombresRegistro == "" ){
        alert("El campo Nombres no debe estar vacío.");
        return false;
    }else if ( apellidosRegistro == "" ){
        alert("El campo Apellidos no debe estar vacío.");
        return false;
    }else if ( correoRegistro == "" ){        
        alert(" El campo del correo electrónico no debe estar vacío.");
        return false;
    }else if ( expReg.test(correoRegistro) == false ){
        alert("No es un correo elctrónico válido.");    
        return false;
    }else if ( passwordRegistro == "" ){
        alert("El campo Contraseña no debe estar vacío.");
        return false;
    }else if ( passwordRegistro.length < 8 ){
        alert("El campo Contraseña debe tener mínimo 8 caracteres");
        return false;
    }

}