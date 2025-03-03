<?php
// Habilitar la visualización de errores
error_reporting(E_ALL);
ini_set('display_errors', 1);

include 'conexion.php';

// Operaciones CRUD para la tabla TipoArbol
if ($_SERVER['REQUEST_METHOD'] == 'POST') {
    if (isset($_POST['crear'])) {
        // Crear un nuevo tipo de árbol
        $nombreCientifico = $_POST['nombre_cientifico'];
        $nombreVulgar = $_POST['nombre_vulgar'];

        $sql = "INSERT INTO TipoArbol (NombreCientifico, NombreVulgar) VALUES (?, ?)";
        $stmt = $conn->prepare($sql);
        $stmt->bind_param("ss", $nombreCientifico, $nombreVulgar);
        if ($stmt->execute()) {
            echo "Tipo de árbol creado correctamente.";
        } else {
            echo "Error al crear el tipo de árbol: " . $stmt->error;
        }
        $stmt->close();
    }

    if (isset($_POST['editar'])) {
        // Actualizar un tipo de árbol existente
        $id = $_POST['id'];
        $nombreCientifico = $_POST['nombre_cientifico'];
        $nombreVulgar = $_POST['nombre_vulgar'];

        $sql = "UPDATE TipoArbol SET NombreCientifico=?, NombreVulgar=? WHERE IDTipoArbol=?";
        $stmt = $conn->prepare($sql);
        $stmt->bind_param("ssi", $nombreCientifico, $nombreVulgar, $id);
        if ($stmt->execute()) {
            echo "Tipo de árbol actualizado correctamente.";
            header("Location: tarbol.php"); // Redirigir para limpiar el formulario
            exit();
        } else {
            echo "Error al actualizar el tipo de árbol: " . $stmt->error;
        }
        $stmt->close();
    }
}

if (isset($_GET['eliminar'])) {
    // Eliminar un tipo de árbol
    $id = $_GET['eliminar'];
    $sql = "DELETE FROM TipoArbol WHERE IDTipoArbol=?";
    $stmt = $conn->prepare($sql);
    $stmt->bind_param("i", $id);
    if ($stmt->execute()) {
        echo "Tipo de árbol eliminado correctamente.";
        header("Location: tarbol.php"); // Redirigir para actualizar la lista
        exit();
    } else {
        echo "Error al eliminar el tipo de árbol: " . $stmt->error;
    }
    $stmt->close();
}

// Obtener todos los tipos de árbol
$sql = "SELECT * FROM TipoArbol";
$resultado = $conn->query($sql);

// Formulario para crear/editar tipos de árbol
echo "<h2>Formulario de Tipo de Árbol</h2>";
echo "<form method='POST'>";
if (isset($_GET['editar'])) {
    $id = $_GET['editar'];
    $sql = "SELECT * FROM TipoArbol WHERE IDTipoArbol=?";
    $stmt = $conn->prepare($sql);
    $stmt->bind_param("i", $id);
    $stmt->execute();
    $result = $stmt->get_result();
    $fila = $result->fetch_assoc();
    echo "<input type='hidden' name='id' value='" . $fila['IDTipoArbol'] . "'>";
    echo "<input type='text' name='nombre_cientifico' value='" . $fila['NombreCientifico'] . "' placeholder='Nombre Científico' required><br>";
    echo "<input type='text' name='nombre_vulgar' value='" . $fila['NombreVulgar'] . "' placeholder='Nombre Vulgar' required><br>";
    echo "<button type='submit' name='editar'>Actualizar Tipo de Árbol</button>";
} else {
    echo "<input type='text' name='nombre_cientifico' placeholder='Nombre Científico' required><br>";
    echo "<input type='text' name='nombre_vulgar' placeholder='Nombre Vulgar' required><br>";
    echo "<button type='submit' name='crear'>Crear Tipo de Árbol</button>";
}
echo "</form>";

// Mostrar la lista de tipos de árbol
if ($resultado->num_rows > 0) {
    echo "<h2>Tipos de Árbol Registrados</h2>";
    echo "<table border='1'>";
    echo "<tr><th>ID</th><th>Nombre Científico</th><th>Nombre Vulgar</th><th>Acciones</th></tr>";
    while ($fila = $resultado->fetch_assoc()) {
        echo "<tr>";
        echo "<td>" . $fila['IDTipoArbol'] . "</td>";
        echo "<td>" . $fila['NombreCientifico'] . "</td>";
        echo "<td>" . $fila['NombreVulgar'] . "</td>";
        echo "<td>
                <a href='?editar=" . $fila['IDTipoArbol'] . "'>Editar</a> |
                <a href='?eliminar=" . $fila['IDTipoArbol'] . "' onclick='return confirm(\"¿Estás seguro de eliminar este tipo de árbol?\");'>Eliminar</a>
              </td>";
        echo "</tr>";
    }
    echo "</table>";
} else {
    echo "No hay tipos de árbol registrados.";
}
?>