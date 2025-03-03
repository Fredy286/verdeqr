<?php
$host = 'localhost';
$usuario = 'root';
$contrasena = '';
$base_de_datos = 'VerdeQR_Optimizada';

// Crear la conexión
$conn = new mysqli($host, $usuario, $contrasena, $base_de_datos);

// Comprobar la conexión
if ($conn->connect_error) {
    die("Conexión fallida: " . $conn->connect_error);
} 
?>