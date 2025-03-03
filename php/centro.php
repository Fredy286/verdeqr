<?php
// Habilitar la visualización de errores
error_reporting(E_ALL);
ini_set('display_errors', 1);

include 'conexion.php';

// Operaciones CRUD para la tabla Centro
if ($_SERVER['REQUEST_METHOD'] == 'POST') {
    if (isset($_POST['crear'])) {
        // Crear un nuevo centro
        $nombre = $_POST['nombre'];
        $descripcion = $_POST['descripcion'];

        $sql = "INSERT INTO Centro (Nombre, Descripcion) VALUES (?, ?)";
        $stmt = $conn->prepare($sql);
        $stmt->bind_param("ss", $nombre, $descripcion);
        if ($stmt->execute()) {
            echo "Centro creado correctamente.";
        } else {
            echo "Error al crear el centro: " . $stmt->error;
        }
        $stmt->close();
    }

    if (isset($_POST['editar'])) {
        // Actualizar un centro existente
        $id = $_POST['id'];
        $nombre = $_POST['nombre'];
        $descripcion = $_POST['descripcion'];

        $sql = "UPDATE Centro SET Nombre=?, Descripcion=? WHERE IDCentro=?";
        $stmt = $conn->prepare($sql);
        $stmt->bind_param("ssi", $nombre, $descripcion, $id);
        if ($stmt->execute()) {
            echo "Centro actualizado correctamente.";
            header("Location: centro.php");
            exit();
        } else {
            echo "Error al actualizar el centro: " . $stmt->error;
        }
        $stmt->close();
    }
}

if (isset($_GET['eliminar'])) {
    // Eliminar un centro
    $id = $_GET['eliminar'];
    $sql = "DELETE FROM Centro WHERE IDCentro=?";
    $stmt = $conn->prepare($sql);
    $stmt->bind_param("i", $id);
    if ($stmt->execute()) {
        echo "Centro eliminado correctamente.";
        header("Location: centro.php");
        exit();
    } else {
        echo "Error al eliminar el centro: " . $stmt->error;
    }
    $stmt->close();
}

// Obtener todos los centros
$sql = "SELECT * FROM Centro";
$resultado = $conn->query($sql);

// Formulario para crear/editar centros
echo "<h2>Formulario de Centro</h2>";
echo "<form method='POST'>";
if (isset($_GET['editar'])) {
    $id = $_GET['editar'];
    $sql = "SELECT * FROM Centro WHERE IDCentro=?";
    $stmt = $conn->prepare($sql);
    $stmt->bind_param("i", $id);
    $stmt->execute();
    $result = $stmt->get_result();
    $fila = $result->fetch_assoc();
    echo "<input type='hidden' name='id' value='" . $fila['IDCentro'] . "'>";
    echo "<input type='text' name='nombre' value='" . $fila['Nombre'] . "' placeholder='Nombre' required><br>";
    echo "<textarea name='descripcion' placeholder='Descripción'>" . $fila['Descripcion'] . "</textarea><br>";
    echo "<button type='submit' name='editar'>Actualizar Centro</button>";
} else {
    echo "<input type='text' name='nombre' placeholder='Nombre' required><br>";
    echo "<textarea name='descripcion' placeholder='Descripción'></textarea><br>";
    echo "<button type='submit' name='crear'>Crear Centro</button>";
}
echo "</form>";

// Mostrar la lista de centros
if ($resultado->num_rows > 0) {
    echo "<h2>Centros Registrados</h2>";
    echo "<table border='1'>";
    echo "<tr><th>ID</th><th>Nombre</th><th>Descripción</th><th>Acciones</th></tr>";
    while ($fila = $resultado->fetch_assoc()) {
        echo "<tr>";
        echo "<td>" . $fila['IDCentro'] . "</td>";
        echo "<td>" . $fila['Nombre'] . "</td>";
        echo "<td>" . $fila['Descripcion'] . "</td>";
        echo "<td>
                <a href='?editar=" . $fila['IDCentro'] . "'>Editar</a> |
                <a href='?eliminar=" . $fila['IDCentro'] . "' onclick='return confirm(\"¿Estás seguro de eliminar este centro?\");'>Eliminar</a>
              </td>";
        echo "</tr>";
    }
    echo "</table>";
} else {
    echo "No hay centros registrados.";
}
?>