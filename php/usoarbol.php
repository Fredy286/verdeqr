<?php
// Habilitar la visualización de errores
error_reporting(E_ALL);
ini_set('display_errors', 1);

include 'conexion.php';

// Operaciones CRUD para la tabla UsoArbol
if ($_SERVER['REQUEST_METHOD'] == 'POST') {
    if (isset($_POST['crear'])) {
        // Crear un nuevo uso de árbol
        $descripcion = $_POST['descripcion'];

        $sql = "INSERT INTO UsoArbol (Descripcion) VALUES (?)";
        $stmt = $conn->prepare($sql);
        $stmt->bind_param("s", $descripcion);
        if ($stmt->execute()) {
            echo "Uso de árbol creado correctamente.";
        } else {
            echo "Error al crear el uso de árbol: " . $stmt->error;
        }
        $stmt->close();
    }

    if (isset($_POST['editar'])) {
        // Actualizar un uso de árbol existente
        $id = $_POST['id'];
        $descripcion = $_POST['descripcion'];

        $sql = "UPDATE UsoArbol SET Descripcion=? WHERE IDUso=?";
        $stmt = $conn->prepare($sql);
        $stmt->bind_param("si", $descripcion, $id);
        if ($stmt->execute()) {
            echo "Uso de árbol actualizado correctamente.";
            header("Location: usoarbol.php");
            exit();
        } else {
            echo "Error al actualizar el uso de árbol: " . $stmt->error;
        }
        $stmt->close();
    }
}

if (isset($_GET['eliminar'])) {
    // Eliminar un uso de árbol
    $id = $_GET['eliminar'];
    $sql = "DELETE FROM UsoArbol WHERE IDUso=?";
    $stmt = $conn->prepare($sql);
    $stmt->bind_param("i", $id);
    if ($stmt->execute()) {
        echo "Uso de árbol eliminado correctamente.";
        header("Location: usoarbol.php");
        exit();
    } else {
        echo "Error al eliminar el uso de árbol: " . $stmt->error;
    }
    $stmt->close();
}

// Obtener todos los usos de árbol
$sql = "SELECT * FROM UsoArbol";
$resultado = $conn->query($sql);

// Formulario para crear/editar usos de árbol
echo "<h2>Formulario de Uso de Árbol</h2>";
echo "<form method='POST'>";
if (isset($_GET['editar'])) {
    $id = $_GET['editar'];
    $sql = "SELECT * FROM UsoArbol WHERE IDUso=?";
    $stmt = $conn->prepare($sql);
    $stmt->bind_param("i", $id);
    $stmt->execute();
    $result = $stmt->get_result();
    $fila = $result->fetch_assoc();
    echo "<input type='hidden' name='id' value='" . $fila['IDUso'] . "'>";
    echo "<input type='text' name='descripcion' value='" . $fila['Descripcion'] . "' placeholder='Descripción' required><br>";
    echo "<button type='submit' name='editar'>Actualizar Uso de Árbol</button>";
} else {
    echo "<input type='text' name='descripcion' placeholder='Descripción' required><br>";
    echo "<button type='submit' name='crear'>Crear Uso de Árbol</button>";
}
echo "</form>";

// Mostrar la lista de usos de árbol
if ($resultado->num_rows > 0) {
    echo "<h2>Usos de Árbol Registrados</h2>";
    echo "<table border='1'>";
    echo "<tr><th>ID</th><th>Descripción</th><th>Acciones</th></tr>";
    while ($fila = $resultado->fetch_assoc()) {
        echo "<tr>";
        echo "<td>" . $fila['IDUso'] . "</td>";
        echo "<td>" . $fila['Descripcion'] . "</td>";
        echo "<td>
                <a href='?editar=" . $fila['IDUso'] . "'>Editar</a> |
                <a href='?eliminar=" . $fila['IDUso'] . "' onclick='return confirm(\"¿Estás seguro de eliminar este uso de árbol?\");'>Eliminar</a>
              </td>";
        echo "</tr>";
    }
    echo "</table>";
} else {
    echo "No hay usos de árbol registrados.";
}
?>