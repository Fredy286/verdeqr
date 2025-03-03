<?php include '../includes/header.php'; ?>

<div class="sidebar">
    <div class="logo">
        <img src="../img/logo.png" alt="Logo VerdeQR" style="width: 100%;">
    </div>
    <ul>
        <li><a href="tarbol.php">Tipos de Árbol</a></li>
        <li><a href="usoarbol.php">Usos del Árbol</a></li>
        <li><a href="tbosque.php">Tipos de Bosque</a></li>
        <li><a href="centro.php">Centros</a></li>
        <li><a href="usuarios.php">Usuarios</a></li>
    </ul>
    <button class="logout">Cerrar Sesión</button>
</div>

<div class="content">
    <div class="topbar">
        <h1>Usuarios</h1>
    </div>

    <div class="main-content">
        <h2>Gestión de Usuarios</h2>
        
        <!-- Formulario para agregar un usuario -->
        <form method="POST" action="../php/usuarios.php">
            <label for="nombres">Nombres:</label>
            <input type="text" id="nombres" name="nombres" required>

            <label for="apellidos">Apellidos:</label>
            <input type="text" id="apellidos" name="apellidos" required>

            <label for="correo">Correo Electrónico:</label>
            <input type="email" id="correo" name="correo" required>

            <label for="contrasena">Contraseña:</label>
            <input type="password" id="contrasena" name="contrasena" required>

            <button type="submit" class="btn">Guardar</button>
        </form>
    </div>
</div>

<?php include '../includes/footer.php'; ?>