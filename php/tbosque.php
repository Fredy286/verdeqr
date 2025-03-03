<?php
// Habilitar la visualización de errores
error_reporting(E_ALL);
ini_set('display_errors', 1);

include 'conexion.php';

// Operaciones CRUD para la tabla TipoBosque
if ($_SERVER['REQUEST_METHOD'] == 'POST') {
    if (isset($_POST['crear'])) {
        // Crear un nuevo tipo de bosque
        $descripcion = $_POST['descripcion'];

        $sql = "INSERT INTO TipoBosque (Descripcion) VALUES (?)";
        $stmt = $conn->prepare($sql);
        $stmt->bind_param("s", $descripcion);
        if ($stmt->execute()) {
            echo "Tipo de bosque creado correctamente.";
        } else {
            echo "Error al crear el tipo de bosque: " . $stmt->error;
        }
        $stmt->close();
    }

    if (isset($_POST['editar'])) {
        // Actualizar un tipo de bosque existente
        $id = $_POST['id'];
        $descripcion = $_POST['descripcion'];

        $sql = "UPDATE TipoBosque SET Descripcion=? WHERE IDTipoBosque=?";
        $stmt = $conn->prepare($sql);
        $stmt->bind_param("si", $descripcion, $id);
        if ($stmt->execute()) {
            echo "Tipo de bosque actualizado correctamente.";
            header("Location: tbosque.php");
            exit();
        } else {
            echo "Error al actualizar el tipo de bosque: " . $stmt->error;
        }
        $stmt->close();
    }
}

if (isset($_GET['eliminar'])) {
    // Eliminar un tipo de bosque
    $id = $_GET['eliminar'];
    $sql = "DELETE FROM TipoBosque WHERE IDTipoBosque=?";
    $stmt = $conn->prepare($sql);
    $stmt->bind_param("i", $id);
    if ($stmt->execute()) {
        echo "Tipo de bosque eliminado correctamente.";
        header("Location: tbosque.php");
        exit();
    } else {
        echo "Error al eliminar el tipo de bosque: " . $stmt->error;
    }
    $stmt->close();
}

// Obtener todos los tipos de bosque
$sql = "SELECT * FROM TipoBosque";
$resultado = $conn->query($sql);

// Formulario para crear/editar tipos de bosque
echo "<h2>Formulario de Tipo de Bosque</h2>";
echo "<form method='POST'>";
if (isset($_GET['editar'])) {
    $id = $_GET['editar'];
    $sql = "SELECT * FROM TipoBosque WHERE IDTipoBosque=?";
    $stmt = $conn->prepare($sql);
    $stmt->bind_param("i", $id);
    $stmt->execute();
    $result = $stmt->get_result();
    $fila = $result->fetch_assoc();
    echo "<input type='hidden' name='id' value='" . $fila['IDTipoBosque'] . "'>";
    echo "<input type='text' name='descripcion' value='" . $fila['Descripcion'] . "' placeholder='Descripción' required><br>";
    echo "<button type='submit' name='editar'>Actualizar Tipo de Bosque</button>";
} else {
    echo "<input type='text' name='descripcion' placeholder='Descripción' required><br>";
    echo "<button type='submit' name='crear'>Crear Tipo de Bosque</button>";
}
echo "</form>";

// Mostrar la lista de tipos de bosque
if ($resultado->num_rows > 0) {
    echo "<h2>Tipos de Bosque Registrados</h2>";
    echo "<table border='1'>";
    echo "<tr><th>ID</th><th>Descripción</th><th>Acciones</th></tr>";
    while ($fila = $resultado->fetch_assoc()) {
        echo "<tr>";
        echo "<td>" . $fila['IDTipoBosque'] . "</td>";
        echo "<td>" . $fila['Descripcion'] . "</td>";
        echo "<td>
                <a href='?editar=" . $fila['IDTipoBosque'] . "'>Editar</a> |
                <a href='?eliminar=" . $fila['IDTipoBosque'] . "' onclick='return confirm(\"¿Estás seguro de eliminar este tipo de bosque?\");'>Eliminar</a>
              </td>";
        echo "</tr>";
    }
    echo "</table>";
} else {
    echo "No hay tipos de bosque registrados.";
}
?>