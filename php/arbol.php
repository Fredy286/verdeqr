<?php
// Habilitar la visualización de errores
error_reporting(E_ALL);
ini_set('display_errors', 1);

include 'conexion.php';

// Obtener datos de las tablas relacionadas
$estados = $conn->query("SELECT * FROM Estado");
$tiposArbol = $conn->query("SELECT * FROM TipoArbol");
$usosArbol = $conn->query("SELECT * FROM UsoArbol");
$tiposBosque = $conn->query("SELECT * FROM TipoBosque");
$centros = $conn->query("SELECT * FROM Centro");

// Operaciones CRUD para la tabla Arbol
if ($_SERVER['REQUEST_METHOD'] == 'POST') {
    if (isset($_POST['crear'])) {
        // Crear un nuevo árbol
        $nombreCientifico = $_POST['nombre_cientifico'];
        $nombreVulgar = $_POST['nombre_vulgar'];
        $ubicacion = $_POST['ubicacion_geografica'];
        $caracteristicas = $_POST['caracteristicas'];
        $servicio = $_POST['servicio_ecosistemico'];
        $cantidad = $_POST['cantidad'];
        $tipoArbol = $_POST['tipo_arbol'];
        $usoArbol = $_POST['uso_arbol'];
        $tipoBosque = $_POST['tipo_bosque'];
        $centro = $_POST['centro'];
        $estado = $_POST['estado'];

        $sql = "INSERT INTO Arbol (NombreCientifico, NombreVulgar, UbicacionGeografica, Caracteristicas, ServicioEcosistemico, Cantidad, TipoArbol, UsoArbol, TipoBosque, Centro, Estado) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)";
        $stmt = $conn->prepare($sql);
        $stmt->bind_param("sssssiiiiii", $nombreCientifico, $nombreVulgar, $ubicacion, $caracteristicas, $servicio, $cantidad, $tipoArbol, $usoArbol, $tipoBosque, $centro, $estado);
        if ($stmt->execute()) {
            echo "Árbol creado correctamente.";
        } else {
            echo "Error al crear el árbol: " . $stmt->error;
        }
        $stmt->close();
    }

    if (isset($_POST['editar'])) {
        // Actualizar un árbol existente
        $id = $_POST['id'];
        $nombreCientifico = $_POST['nombre_cientifico'];
        $nombreVulgar = $_POST['nombre_vulgar'];
        $ubicacion = $_POST['ubicacion_geografica'];
        $caracteristicas = $_POST['caracteristicas'];
        $servicio = $_POST['servicio_ecosistemico'];
        $cantidad = $_POST['cantidad'];
        $tipoArbol = $_POST['tipo_arbol'];
        $usoArbol = $_POST['uso_arbol'];
        $tipoBosque = $_POST['tipo_bosque'];
        $centro = $_POST['centro'];
        $estado = $_POST['estado'];

        $sql = "UPDATE Arbol SET NombreCientifico=?, NombreVulgar=?, UbicacionGeografica=?, Caracteristicas=?, ServicioEcosistemico=?, Cantidad=?, TipoArbol=?, UsoArbol=?, TipoBosque=?, Centro=?, Estado=? WHERE IDArbol=?";
        $stmt = $conn->prepare($sql);
        $stmt->bind_param("sssssiiiiiii", $nombreCientifico, $nombreVulgar, $ubicacion, $caracteristicas, $servicio, $cantidad, $tipoArbol, $usoArbol, $tipoBosque, $centro, $estado, $id);
        if ($stmt->execute()) {
            echo "Árbol actualizado correctamente.";
            // Redirigir para limpiar el formulario
            header("Location: arbol.php");
            exit();
        } else {
            echo "Error al actualizar el árbol: " . $stmt->error;
        }
        $stmt->close();
    }
}

if (isset($_GET['eliminar'])) {
    // Eliminar un árbol
    $id = $_GET['eliminar'];
    $sql = "DELETE FROM Arbol WHERE IDArbol=?";
    $stmt = $conn->prepare($sql);
    $stmt->bind_param("i", $id);
    if ($stmt->execute()) {
        echo "Árbol eliminado correctamente.";
        // Redirigir para actualizar la lista
        header("Location: arbol.php");
        exit();
    } else {
        echo "Error al eliminar el árbol: " . $stmt->error;
    }
    $stmt->close();
}

// Obtener todos los árboles con detalles de las tablas relacionadas
$sql = "SELECT 
            a.IDArbol, 
            a.NombreCientifico, 
            a.NombreVulgar, 
            a.UbicacionGeografica, 
            a.Caracteristicas, 
            a.ServicioEcosistemico, 
            a.Cantidad, 
            ta.NombreCientifico AS TipoArbolNombre, 
            ta.NombreVulgar AS TipoArbolVulgar, 
            ua.Descripcion AS UsoArbolDescripcion, 
            tb.Descripcion AS TipoBosqueDescripcion, 
            c.Nombre AS CentroNombre, 
            e.Descripcion AS EstadoDescripcion
        FROM Arbol a
        JOIN TipoArbol ta ON a.TipoArbol = ta.IDTipoArbol
        JOIN UsoArbol ua ON a.UsoArbol = ua.IDUso
        JOIN TipoBosque tb ON a.TipoBosque = tb.IDTipoBosque
        JOIN Centro c ON a.Centro = c.IDCentro
        JOIN Estado e ON a.Estado = e.IDEstado";
$resultado = $conn->query($sql);

// Formulario para crear/editar árboles
echo "<h2>Formulario de Árbol</h2>";
echo "<form method='POST'>";
if (isset($_GET['editar'])) {
    $id = $_GET['editar'];
    $sql = "SELECT * FROM Arbol WHERE IDArbol=?";
    $stmt = $conn->prepare($sql);
    $stmt->bind_param("i", $id);
    $stmt->execute();
    $result = $stmt->get_result();
    $fila = $result->fetch_assoc();
    echo "<input type='hidden' name='id' value='" . $fila['IDArbol'] . "'>";
    echo "<input type='text' name='nombre_cientifico' value='" . $fila['NombreCientifico'] . "' placeholder='Nombre Científico' required><br>";
    echo "<input type='text' name='nombre_vulgar' value='" . $fila['NombreVulgar'] . "' placeholder='Nombre Vulgar'><br>";
    echo "<input type='text' name='ubicacion_geografica' value='" . $fila['UbicacionGeografica'] . "' placeholder='Ubicación Geográfica'><br>";
    echo "<textarea name='caracteristicas' placeholder='Características'>" . $fila['Caracteristicas'] . "</textarea><br>";
    echo "<input type='text' name='servicio_ecosistemico' value='" . $fila['ServicioEcosistemico'] . "' placeholder='Servicio Ecosistémico'><br>";
    echo "<input type='number' name='cantidad' value='" . $fila['Cantidad'] . "' placeholder='Cantidad'><br>";

    // Lista desplegable para Tipo de Árbol
    echo "<select name='tipo_arbol' required>";
    while ($tipo = $tiposArbol->fetch_assoc()) {
        $selected = ($tipo['IDTipoArbol'] == $fila['TipoArbol']) ? "selected" : "";
        echo "<option value='" . $tipo['IDTipoArbol'] . "' $selected>" . $tipo['NombreCientifico'] . " (" . $tipo['NombreVulgar'] . ")</option>";
    }
    echo "</select><br>";

    // Lista desplegable para Uso del Árbol
    echo "<select name='uso_arbol' required>";
    while ($uso = $usosArbol->fetch_assoc()) {
        $selected = ($uso['IDUso'] == $fila['UsoArbol']) ? "selected" : "";
        echo "<option value='" . $uso['IDUso'] . "' $selected>" . $uso['Descripcion'] . "</option>";
    }
    echo "</select><br>";

    // Lista desplegable para Tipo de Bosque
    echo "<select name='tipo_bosque' required>";
    while ($bosque = $tiposBosque->fetch_assoc()) {
        $selected = ($bosque['IDTipoBosque'] == $fila['TipoBosque']) ? "selected" : "";
        echo "<option value='" . $bosque['IDTipoBosque'] . "' $selected>" . $bosque['Descripcion'] . "</option>";
    }
    echo "</select><br>";

    // Lista desplegable para Centro
    echo "<select name='centro' required>";
    while ($centro = $centros->fetch_assoc()) {
        $selected = ($centro['IDCentro'] == $fila['Centro']) ? "selected" : "";
        echo "<option value='" . $centro['IDCentro'] . "' $selected>" . $centro['Nombre'] . "</option>";
    }
    echo "</select><br>";

    // Lista desplegable para Estado
    echo "<select name='estado' required>";
    while ($estado = $estados->fetch_assoc()) {
        $selected = ($estado['IDEstado'] == $fila['Estado']) ? "selected" : "";
        echo "<option value='" . $estado['IDEstado'] . "' $selected>" . $estado['Descripcion'] . "</option>";
    }
    echo "</select><br>";

    echo "<button type='submit' name='editar'>Actualizar Árbol</button>";
} else {
    echo "<input type='text' name='nombre_cientifico' placeholder='Nombre Científico' required><br>";
    echo "<input type='text' name='nombre_vulgar' placeholder='Nombre Vulgar'><br>";
    echo "<input type='text' name='ubicacion_geografica' placeholder='Ubicación Geográfica'><br>";
    echo "<textarea name='caracteristicas' placeholder='Características'></textarea><br>";
    echo "<input type='text' name='servicio_ecosistemico' placeholder='Servicio Ecosistémico'><br>";
    echo "<input type='number' name='cantidad' placeholder='Cantidad'><br>";

    // Lista desplegable para Tipo de Árbol
    echo "<select name='tipo_arbol' required>";
    while ($tipo = $tiposArbol->fetch_assoc()) {
        echo "<option value='" . $tipo['IDTipoArbol'] . "'>" . $tipo['NombreCientifico'] . " (" . $tipo['NombreVulgar'] . ")</option>";
    }
    echo "</select><br>";

    // Lista desplegable para Uso del Árbol
    echo "<select name='uso_arbol' required>";
    while ($uso = $usosArbol->fetch_assoc()) {
        echo "<option value='" . $uso['IDUso'] . "'>" . $uso['Descripcion'] . "</option>";
    }
    echo "</select><br>";

    // Lista desplegable para Tipo de Bosque
    echo "<select name='tipo_bosque' required>";
    while ($bosque = $tiposBosque->fetch_assoc()) {
        echo "<option value='" . $bosque['IDTipoBosque'] . "'>" . $bosque['Descripcion'] . "</option>";
    }
    echo "</select><br>";

    // Lista desplegable para Centro
    echo "<select name='centro' required>";
    while ($centro = $centros->fetch_assoc()) {
        echo "<option value='" . $centro['IDCentro'] . "'>" . $centro['Nombre'] . "</option>";
    }
    echo "</select><br>";

    // Lista desplegable para Estado
    echo "<select name='estado' required>";
    while ($estado = $estados->fetch_assoc()) {
        echo "<option value='" . $estado['IDEstado'] . "'>" . $estado['Descripcion'] . "</option>";
    }
    echo "</select><br>";

    echo "<button type='submit' name='crear'>Crear Árbol</button>";
}
echo "</form>";

// Mostrar la lista de árboles con detalles
if ($resultado->num_rows > 0) {
    echo "<h2>Árboles Registrados</h2>";
    echo "<table border='1'>";
    echo "<tr>
            <th>ID</th>
            <th>Nombre Científico</th>
            <th>Nombre Vulgar</th>
            <th>Ubicación</th>
            <th>Características</th>
            <th>Servicio Ecosistémico</th>
            <th>Cantidad</th>
            <th>Tipo de Árbol</th>
            <th>Uso del Árbol</th>
            <th>Tipo de Bosque</th>
            <th>Centro</th>
            <th>Estado</th>
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
        echo "<td>" . $fila['TipoArbolNombre'] . " (" . $fila['TipoArbolVulgar'] . ")</td>";
        echo "<td>" . $fila['UsoArbolDescripcion'] . "</td>";
        echo "<td>" . $fila['TipoBosqueDescripcion'] . "</td>";
        echo "<td>" . $fila['CentroNombre'] . "</td>";
        echo "<td>" . $fila['EstadoDescripcion'] . "</td>";
        echo "<td>
                <a href='?editar=" . $fila['IDArbol'] . "'>Editar</a> |
                <a href='?eliminar=" . $fila['IDArbol'] . "' onclick='return confirm(\"¿Estás seguro de eliminar este árbol?\");'>Eliminar</a>
              </td>";
        echo "</tr>";
    }
    echo "</table>";
} else {
    echo "No hay árboles registrados.";
}
?>