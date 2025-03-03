<?php
// Habilitar la visualización de errores
error_reporting(E_ALL);
ini_set('display_errors', 1);

include 'conexion.php';

// Operaciones CRUD para la tabla Estado
if ($_SERVER['REQUEST_METHOD'] == 'POST') {
    if (isset($_POST['crear'])) {
        // Crear un nuevo estado
        $descripcion = $_POST['descripcion'];

        $sql = "INSERT INTO Estado (Descripcion) VALUES (?)";
        $stmt = $conn->prepare($sql);
        $stmt->bind_param("s", $descripcion);
        if ($stmt->execute()) {
            echo "Estado creado correctamente.";
        } else {
            echo "Error al crear el estado: " . $stmt->error;
        }
        $stmt->close();
    }

    if (isset($_POST['editar'])) {
        // Actualizar un estado existente
        $id = $_POST['id'];
        $descripcion = $_POST['descripcion'];

        $sql = "UPDATE Estado SET Descripcion=? WHERE IDEstado=?";
        $stmt = $conn->prepare($sql);
        $stmt->bind_param("si", $descripcion, $id);
        if ($stmt->execute()) {
            echo "Estado actualizado correctamente.";
            header("Location: estado.php");
            exit();
        } else {
            echo "Error al actualizar el estado: " . $stmt->error;
        }
        $stmt->close();
    }
}

if (isset($_GET['eliminar'])) {
    // Eliminar un estado
    $id = $_GET['eliminar'];
    $sql = "DELETE FROM Estado WHERE IDEstado=?";
    $stmt = $conn->prepare($sql);
    $stmt->bind_param("i", $id);
    if ($stmt->execute()) {
        echo "Estado eliminado correctamente.";
        header("Location: estado.php");
        exit();
    } else {
        echo "Error al eliminar el estado: " . $stmt->error;
    }
    $stmt->close();
}

// Obtener todos los estados
$sql = "SELECT * FROM Estado";
$resultado = $conn->query($sql);

// Formulario para crear/editar estados
echo "<h2>Formulario de Estado</h2>";
echo "<form method='POST'>";
if (isset($_GET['editar'])) {
    $id = $_GET['editar'];
    $sql = "SELECT * FROM Estado WHERE IDEstado=?";
    $stmt = $conn->prepare($sql);
    $stmt->bind_param("i", $id);
    $stmt->execute();
    $result = $stmt->get_result();
    $fila = $result->fetch_assoc();
    echo "<input type='hidden' name='id' value='" . $fila['IDEstado'] . "'>";
    echo "<input type='text' name='descripcion' value='" . $fila['Descripcion'] . "' placeholder='Descripción' required><br>";
    echo "<button type='submit' name='editar'>Actualizar Estado</button>";
} else {
    echo "<input type='text' name='descripcion' placeholder='Descripción' required><br>";
    echo "<button type='submit' name='crear'>Crear Estado</button>";
}
echo "</form>";

// Mostrar la lista de estados
if ($resultado->num_rows > 0) {
    echo "<h2>Estados Registrados</h2>";
    echo "<table border='1'>";
    echo "<tr><th>ID</th><th>Descripción</th><th>Acciones</th></tr>";
    while ($fila = $resultado->fetch_assoc()) {
        echo "<tr>";
        echo "<td>" . $fila['IDEstado'] . "</td>";
        echo "<td>" . $fila['Descripcion'] . "</td>";
        echo "<td>
                <a href='?editar=" . $fila['IDEstado'] . "'>Editar</a> |
                <a href='?eliminar=" . $fila['IDEstado'] . "' onclick='return confirm(\"¿Estás seguro de eliminar este estado?\");'>Eliminar</a>
              </td>";
        echo "</tr>";
    }
    echo "</table>";
} else {
    echo "No hay estados registrados.";
}
?>