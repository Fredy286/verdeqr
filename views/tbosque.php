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
        <h1>Tipos de Bosque</h1>
    </div>

    <div class="main-content">
        <h2>Gestión de Tipos de Bosque</h2>
        
        <!-- Formulario para agregar un tipo de bosque -->
        <form method="POST" action="../php/tbosque.php">
            <label for="descripcion">Descripción:</label>
            <input type="text" id="descripcion" name="descripcion" required>

            <button type="submit" class="btn">Guardar</button>
        </form>
    </div>
</div>

<?php include '../includes/footer.php'; ?>