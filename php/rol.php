<?php
include 'conexion.php';

// Operaciones CRUD para la tabla Rol
if ($_SERVER['REQUEST_METHOD'] == 'POST') {
    if (isset($_POST['crear'])) {
        // Crear un nuevo rol
        $nombre = $_POST['nombre'];
        $descripcion = $_POST['descripcion'];

        $sql = "INSERT INTO Rol (Nombre, Descripcion) VALUES (?, ?)";
        $stmt = $conn->prepare($sql);
        $stmt->bind_param("ss", $nombre, $descripcion);

        if ($stmt->execute()) {
            echo "Rol creado correctamente.";
        } else {
            echo "Error al crear el rol: " . $stmt->error;
        }
        $stmt->close();
    }

    if (isset($_POST['editar'])) {
        // Actualizar un rol existente
        $id = $_POST['id'];
        $nombre = $_POST['nombre'];
        $descripcion = $_POST['descripcion'];

        $sql = "UPDATE Rol SET Nombre=?, Descripcion=? WHERE IDRol=?";
        $stmt = $conn->prepare($sql);
        $stmt->bind_param("ssi", $nombre, $descripcion, $id);

        if ($stmt->execute()) {
            echo "Rol actualizado correctamente.";
            header("Location: rol.php");
            exit();
        } else {
            echo "Error al actualizar el rol: " . $stmt->error;
        }
        $stmt->close();
    }
}

if (isset($_GET['eliminar'])) {
    // Eliminar un rol
    $id = $_GET['eliminar'];
    $sql = "DELETE FROM Rol WHERE IDRol=?";
    $stmt = $conn->prepare($sql);
    $stmt->bind_param("i", $id);

    if ($stmt->execute()) {
        echo "Rol eliminado correctamente.";
        header("Location: rol.php");
        exit();
    } else {
        echo "Error al eliminar el rol: " . $stmt->error;
    }
    $stmt->close();
}

// Obtener todos los roles
$sql = "SELECT * FROM Rol";
$resultado = $conn->query($sql);

// Formulario para crear/editar roles
echo "<h2>Formulario de Rol</h2>";
echo "<form method='POST'>";
if (isset($_GET['editar'])) {
    $id = $_GET['editar'];
    $sql = "SELECT * FROM Rol WHERE IDRol=?";
    $stmt = $conn->prepare($sql);
    $stmt->bind_param("i", $id);
    $stmt->execute();
    $result = $stmt->get_result();
    $fila = $result->fetch_assoc();

    echo "<input type='hidden' name='id' value='" . $fila['IDRol'] . "'>";
    echo "<input type='text' name='nombre' value='" . $fila['Nombre'] . "' placeholder='Nombre' required><br>";
    echo "<textarea name='descripcion' placeholder='Descripción'>" . $fila['Descripcion'] . "</textarea><br>";
    echo "<button type='submit' name='editar'>Actualizar Rol</button>";
} else {
    echo "<input type='text' name='nombre' placeholder='Nombre' required><br>";
    echo "<textarea name='descripcion' placeholder='Descripción'></textarea><br>";
    echo "<button type='submit' name='crear'>Crear Rol</button>";
}
echo "</form>";

// Mostrar la lista de roles
if ($resultado->num_rows > 0) {
    echo "<h2>Roles Registrados</h2>";
    echo "<table border='1'>";
    echo "<tr>
            <th>ID</th>
            <th>Nombre</th>
            <th>Descripción</th>
            <th>Acciones</th>
          </tr>";
    while ($fila = $resultado->fetch_assoc()) {
        echo "<tr>";
        echo "<td>" . $fila['IDRol'] . "</td>";
        echo "<td>" . $fila['Nombre'] . "</td>";
        echo "<td>" . $fila['Descripcion'] . "</td>";
        echo "<td>
                <a href='?editar=" . $fila['IDRol'] . "'>Editar</a> |
                <a href='?eliminar=" . $fila['IDRol'] . "' onclick='return confirm(\"¿Estás seguro de eliminar este rol?\");'>Eliminar</a>
              </td>";
        echo "</tr>";
    }
    echo "</table>";
} else {
    echo "No hay roles registrados.";
}
?>