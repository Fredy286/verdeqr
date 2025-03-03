<?php
include 'conexion.php';

// Obtener datos de la tabla Estado
$estados = $conn->query("SELECT * FROM Estado");

// Operaciones CRUD para la tabla Usuario
if ($_SERVER['REQUEST_METHOD'] == 'POST') {
    if (isset($_POST['crear'])) {
        // Crear un nuevo usuario
        $nombres = $_POST['nombres'];
        $apellidos = $_POST['apellidos'];
        $correo = $_POST['correo'];
        $telefono = $_POST['telefono'];
        $contrasena = password_hash($_POST['contrasena'], PASSWORD_DEFAULT); // Encriptar contraseña
        $estado = $_POST['estado'];

        $sql = "INSERT INTO Usuario (Nombres, Apellidos, CorreoElectronico, Telefono, Contrasena, Estado) 
                VALUES (?, ?, ?, ?, ?, ?)";
        $stmt = $conn->prepare($sql);
        $stmt->bind_param("sssssi", $nombres, $apellidos, $correo, $telefono, $contrasena, $estado);

        if ($stmt->execute()) {
            echo "Usuario creado correctamente.";
        } else {
            echo "Error al crear el usuario: " . $stmt->error;
        }
        $stmt->close();
    }

    if (isset($_POST['editar'])) {
        // Actualizar un usuario existente
        $id = $_POST['id'];
        $nombres = $_POST['nombres'];
        $apellidos = $_POST['apellidos'];
        $correo = $_POST['correo'];
        $telefono = $_POST['telefono'];
        $estado = $_POST['estado'];

        $sql = "UPDATE Usuario SET Nombres=?, Apellidos=?, CorreoElectronico=?, Telefono=?, Estado=? 
                WHERE IDUsuario=?";
        $stmt = $conn->prepare($sql);
        $stmt->bind_param("ssssii", $nombres, $apellidos, $correo, $telefono, $estado, $id);

        if ($stmt->execute()) {
            echo "Usuario actualizado correctamente.";
            header("Location: usuario.php");
            exit();
        } else {
            echo "Error al actualizar el usuario: " . $stmt->error;
        }
        $stmt->close();
    }
}

if (isset($_GET['eliminar'])) {
    // Eliminar un usuario
    $id = $_GET['eliminar'];
    $sql = "DELETE FROM Usuario WHERE IDUsuario=?";
    $stmt = $conn->prepare($sql);
    $stmt->bind_param("i", $id);

    if ($stmt->execute()) {
        echo "Usuario eliminado correctamente.";
        header("Location: usuario.php");
        exit();
    } else {
        echo "Error al eliminar el usuario: " . $stmt->error;
    }
    $stmt->close();
}

// Obtener todos los usuarios con detalles de Estado
$sql = "SELECT u.*, e.Descripcion AS EstadoDescripcion 
        FROM Usuario u 
        JOIN Estado e ON u.Estado = e.IDEstado";
$resultado = $conn->query($sql);

// Formulario para crear/editar usuarios
echo "<h2>Formulario de Usuario</h2>";
echo "<form method='POST'>";
if (isset($_GET['editar'])) {
    $id = $_GET['editar'];
    $sql = "SELECT * FROM Usuario WHERE IDUsuario=?";
    $stmt = $conn->prepare($sql);
    $stmt->bind_param("i", $id);
    $stmt->execute();
    $result = $stmt->get_result();
    $fila = $result->fetch_assoc();

    echo "<input type='hidden' name='id' value='" . $fila['IDUsuario'] . "'>";
    echo "<input type='text' name='nombres' value='" . $fila['Nombres'] . "' placeholder='Nombres' required><br>";
    echo "<input type='text' name='apellidos' value='" . $fila['Apellidos'] . "' placeholder='Apellidos' required><br>";
    echo "<input type='email' name='correo' value='" . $fila['CorreoElectronico'] . "' placeholder='Correo' required><br>";
    echo "<input type='text' name='telefono' value='" . $fila['Telefono'] . "' placeholder='Teléfono'><br>";

    // Lista desplegable para Estado
    echo "<select name='estado' required>";
    while ($estado = $estados->fetch_assoc()) {
        $selected = ($estado['IDEstado'] == $fila['Estado']) ? "selected" : "";
        echo "<option value='" . $estado['IDEstado'] . "' $selected>" . $estado['Descripcion'] . "</option>";
    }
    echo "</select><br>";

    echo "<button type='submit' name='editar'>Actualizar Usuario</button>";
} else {
    echo "<input type='text' name='nombres' placeholder='Nombres' required><br>";
    echo "<input type='text' name='apellidos' placeholder='Apellidos' required><br>";
    echo "<input type='email' name='correo' placeholder='Correo' required><br>";
    echo "<input type='text' name='telefono' placeholder='Teléfono'><br>";
    echo "<input type='password' name='contrasena' placeholder='Contraseña' required><br>";

    // Lista desplegable para Estado
    echo "<select name='estado' required>";
    while ($estado = $estados->fetch_assoc()) {
        echo "<option value='" . $estado['IDEstado'] . "'>" . $estado['Descripcion'] . "</option>";
    }
    echo "</select><br>";

    echo "<button type='submit' name='crear'>Crear Usuario</button>";
}
echo "</form>";

// Mostrar la lista de usuarios
if ($resultado->num_rows > 0) {
    echo "<h2>Usuarios Registrados</h2>";
    echo "<table border='1'>";
    echo "<tr>
            <th>ID</th>
            <th>Nombres</th>
            <th>Apellidos</th>
            <th>Correo</th>
            <th>Teléfono</th>
            <th>Estado</th>
            <th>Acciones</th>
          </tr>";
    while ($fila = $resultado->fetch_assoc()) {
        echo "<tr>";
        echo "<td>" . $fila['IDUsuario'] . "</td>";
        echo "<td>" . $fila['Nombres'] . "</td>";
        echo "<td>" . $fila['Apellidos'] . "</td>";
        echo "<td>" . $fila['CorreoElectronico'] . "</td>";
        echo "<td>" . $fila['Telefono'] . "</td>";
        echo "<td>" . $fila['EstadoDescripcion'] . "</td>";
        echo "<td>
                <a href='?editar=" . $fila['IDUsuario'] . "'>Editar</a> |
                <a href='?eliminar=" . $fila['IDUsuario'] . "' onclick='return confirm(\"¿Estás seguro de eliminar este usuario?\");'>Eliminar</a>
              </td>";
        echo "</tr>";
    }
    echo "</table>";
} else {
    echo "No hay usuarios registrados.";
}
?>