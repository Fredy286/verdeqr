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
        <h1>Tipos de Árbol</h1>
    </div>

    <div class="main-content">
        <h2>Gestión de Tipos de Árbol</h2>
        
        <!-- Formulario para agregar un tipo de árbol -->
        <form method="POST" action="../php/tarbol.php">
            <label for="nombre_cientifico">Nombre Científico:</label>
            <input type="text" id="nombre_cientifico" name="nombre_cientifico" required>

            <label for="nombre_vulgar">Nombre Vulgar:</label>
            <input type="text" id="nombre_vulgar" name="nombre_vulgar" required>

            <button type="submit" class="btn">Guardar</button>
        </form>
    </div>
</div>

<?php include '../includes/footer.php'; ?>