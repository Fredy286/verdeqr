<?php include '../includes/header.php'; ?>

<!-- Menú lateral para el panel de administrador -->
<div class="sidebar">
    <div class="logo">
        <img src="../img/logo.png" alt="Logo VerdeQR" style="width: 100%;">
    </div>
    <ul>
        <li><a href="arbol.php">Registrar Árbol</a></li>
        <li><a href="tarbol.php">Tipos de Árbol</a></li>
        <li><a href="usoarbol.php">Usos del Árbol</a></li>
        <li><a href="tbosque.php">Tipos de Bosque</a></li>
        <li><a href="centro.php">Centros</a></li>
        <li><a href="usuarios.php">Usuarios</a></li>
    </ul>
    <button class="logout">Cerrar Sesión</button>
</div>

<!-- Contenido principal -->
<div class="content">
    <div class="topbar">
        <h1>Panel de Administrador</h1>
    </div>

    <div class="main-content">
        <h2>Bienvenido al Panel de Administrador</h2>
        <p>Selecciona una opción del menú lateral para comenzar.</p>
    </div>
</div>

<?php include '../includes/footer.php'; ?>