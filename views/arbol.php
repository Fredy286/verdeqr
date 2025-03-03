<?php include '../includes/header.php'; ?>

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

<div class="content">
    <div class="topbar">
        <h1>Registrar Árbol</h1>
    </div>

    <div class="main-content">
        <h2>Gestión de Árboles</h2>
        
        <!-- Formulario para agregar un árbol -->
        <form method="POST" action="../php/arbol.php">
            <label for="nombre_cientifico">Nombre Científico:</label>
            <input type="text" id="nombre_cientifico" name="nombre_cientifico" required>

            <label for="nombre_vulgar">Nombre Vulgar:</label>
            <input type="text" id="nombre_vulgar" name="nombre_vulgar" required>

            <label for="ubicacion_geografica">Ubicación Geográfica:</label>
            <input type="text" id="ubicacion_geografica" name="ubicacion_geografica" required>

            <label for="caracteristicas">Características:</label>
            <textarea id="caracteristicas" name="caracteristicas" required></textarea>

            <label for="servicio_ecosistemico">Servicio Ecosistémico:</label>
            <input type="text" id="servicio_ecosistemico" name="servicio_ecosistemico" required>

            <label for="cantidad">Cantidad:</label>
            <input type="number" id="cantidad" name="cantidad" required>

            <!-- Campos para las medidas del árbol -->
            <label for="cap">CAP (cm):</label>
            <input type="number" id="cap" name="cap" step="0.01" required>

            <label for="dap">DAP (m):</label>
            <input type="number" id="dap" name="dap" step="0.01" required>

            <label for="altura_comercial">Altura Comercial (m):</label>
            <input type="number" id="altura_comercial" name="altura_comercial" step="0.01" required>

            <label for="altura_total">Altura Total (m):</label>
            <input type="number" id="altura_total" name="altura_total" step="0.01" required>

            <label for="area_basal">Área Basal (m²):</label>
            <input type="number" id="area_basal" name="area_basal" step="0.01" required>

            <button type="submit" name="crear" class="btn">Guardar Árbol</button>
        </form>

        <!-- Mostrar la lista de árboles con medidas -->
        <?php
        include '../includes/conexion.php';
        $sql = "SELECT 
                    a.IDArbol, 
                    a.NombreCientifico, 
                    a.NombreVulgar, 
                    a.UbicacionGeografica, 
                    a.Caracteristicas, 
                    a.ServicioEcosistemico, 
                    a.Cantidad, 
                    m.CAP, 
                    m.DAP, 
                    m.AlturaComercial, 
                    m.AlturaTotal, 
                    m.AreaBasal
                FROM Arbol a
                JOIN MedidasArbol m ON a.MedidasArbol = m.IDMedida";
        $resultado = $conn->query($sql);

        if ($resultado->num_rows > 0) {
            echo "<h2>Árboles Registrados</h2>";
            echo "<table>";
            echo "<tr>
                    <th>ID</th>
                    <th>Nombre Científico</th>
                    <th>Nombre Vulgar</th>
                    <th>Ubicación</th>
                    <th>Características</th>
                    <th>Servicio Ecosistémico</th>
                    <th>Cantidad</th>
                    <th>CAP (cm)</th>
                    <th>DAP (m)</th>
                    <th>Altura Comercial (m)</th>
                    <th>Altura Total (m)</th>
                    <th>Área Basal (m²)</th>
                    <th>Acciones</th>
                  </tr>";
            while ($fila = $resultado->fetch_assoc()) {
                echo "<tr>";
                echo "<td>" . $fila['IDArbol'] . "</td>";
                echo "<td>" . $fila['NombreCientifico'] . "</td>";
                echo "<td>" . $fila['NombreVulgar'] . "</td>";
                echo "<td>" . $fila['UbicacionGeografica'] . "</td>";
                echo "<td>" . $fila['Caracteristicas'] . "</td>";
                echo "<td>" . $fila['ServicioEcosistemico'] . "</td>";
                echo "<td>" . $fila['Cantidad'] . "</td>";
                echo "<td>" . $fila['CAP'] . "</td>";
                echo "<td>" . $fila['DAP'] . "</td>";
                echo "<td>" . $fila['AlturaComercial'] . "</td>";
                echo "<td>" . $fila['AlturaTotal'] . "</td>";
                echo "<td>" . $fila['AreaBasal'] . "</td>";
                echo "<td>
                        <a href='?editar=" . $fila['IDArbol'] . "'>Editar</a> |
                        <a href='?eliminar=" . $fila['IDArbol'] . "' onclick='return confirm(\"¿Estás seguro de eliminar este árbol?\");'>Eliminar</a>
                      </td>";
                echo "</tr>";
            }
            echo "</table>";
        } else {
            echo "<p>No hay árboles registrados.</p>";
        }
        ?>
    </div>
</div>

<?php include '../includes/footer.php'; ?>