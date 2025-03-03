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
        <h1>Centros</h1>
    </div>

    <div class="main-content">
        <h2>Gestión de Centros</h2>
        
        <!-- Formulario para agregar un centro -->
        <form method="POST" action="../php/centro.php">
            <label for="nombre">Nombre:</label>
            <input type="text" id="nombre" name="nombre" required>

            <label for="descripcion">Descripción:</label>
            <textarea id="descripcion" name="descripcion" required></textarea>

            <button type="submit" class="btn">Guardar</button>
        </form>
    </div>
</div>

<?php include '../includes/footer.php'; ?>