<?php
// Habilitar la visualización de errores (desactivar en producción)
error_reporting(E_ALL);
ini_set('display_errors', 1);

// Incluir archivo de conexión a la base de datos
include 'conexion.php';

// Inicializar variables para limpiar el formulario
$usuario = "";
$titulo = "";
$descripcion = "";
$mensaje = "";  // Para mostrar mensajes de éxito/error

// ****************************************************************************
// PROCESAMIENTO DE FORMULARIO (Crear/Actualizar)
// ****************************************************************************
if ($_SERVER['REQUEST_METHOD'] == 'POST') {
    if (isset($_POST['crear'])) {
        // CREAR una nueva sugerencia
        $usuario = $_POST['usuario'];
        $titulo = $_POST['titulo'];
        $descripcion = $_POST['descripcion'];

        $sql = "INSERT INTO Sugerencia (Usuario, Titulo, Descripcion) VALUES (?, ?, ?)";
        $stmt = $conn->prepare($sql);
        $stmt->bind_param("iss", $usuario, $titulo, $descripcion);

        if ($stmt->execute()) {
            $mensaje = "<p style='color: green;'>Sugerencia creada correctamente.</p>";

            // Limpiar las variables del formulario
            $usuario = "";
            $titulo = "";
            $descripcion = "";
        } else {
            $mensaje = "<p style='color: red;'>Error al crear la sugerencia: " . $stmt->error . "</p>";
        }
        $stmt->close();
    }

    if (isset($_POST['editar'])) {
        // ACTUALIZAR una sugerencia existente
        $id = $_POST['id'];
        $usuario = $_POST['usuario'];
        $titulo = $_POST['titulo'];
        $descripcion = $_POST['descripcion'];

        $sql = "UPDATE Sugerencia SET Usuario=?, Titulo=?, Descripcion=? WHERE IDSugerencia=?";
        $stmt = $conn->prepare($sql);
        $stmt->bind_param("issi", $usuario, $titulo, $descripcion, $id);

        if ($stmt->execute()) {
            $mensaje = "<p style='color: green;'>Sugerencia actualizada correctamente.</p>";

            // Limpiar las variables del formulario
            $usuario = "";
            $titulo = "";
            $descripcion = "";

            // Redirigir para evitar problemas al recargar la página
            header("Location: sugerencias.php");
            exit;
        } else {
            $mensaje = "<p style='color: red;'>Error al actualizar la sugerencia: " . $stmt->error . "</p>";
        }
        $stmt->close();
    }
}

// ****************************************************************************
// ELIMINAR Sugerencia
// ****************************************************************************
if (isset($_GET['eliminar'])) {
    $id = $_GET['eliminar'];
    $sql = "DELETE FROM Sugerencia WHERE IDSugerencia=?";
    $stmt = $conn->prepare($sql);
    $stmt->bind_param("i", $id);

    if ($stmt->execute()) {
        $mensaje = "<p style='color: green;'>Sugerencia eliminada correctamente.</p>";
    } else {
        $mensaje = "<p style='color: red;'>Error al eliminar la sugerencia: " . $stmt->error . "</p>";
    }
    $stmt->close();

    // Redirigir para evitar problemas al recargar la página
    header("Location: sugerencias.php");
    exit;
}

// ****************************************************************************
// OBTENER DATOS para el formulario y la lista
// ****************************************************************************

// Obtener lista de usuarios para el select
$usuarios = $conn->query("SELECT IDUsuario, Nombres, Apellidos FROM Usuario");

// Obtener todas las sugerencias
$sql = "SELECT S.IDSugerencia, S.Titulo, S.Descripcion, U.Nombres, U.Apellidos
        FROM Sugerencia S
        JOIN Usuario U ON S.Usuario = U.IDUsuario";
$resultado = $conn->query($sql);

// ****************************************************************************
// FORMULARIO para crear/editar Sugerencias
// ****************************************************************************
echo "<h2>Formulario de Sugerencias</h2>";
echo "<form method='POST'>";

// Mostrar mensajes de éxito/error
echo $mensaje;

// Si estamos editando, cargar los datos de la sugerencia
if (isset($_GET['editar'])) {
    $id = $_GET['editar'];
    $sql = "SELECT * FROM Sugerencia WHERE IDSugerencia=?";
    $stmt = $conn->prepare($sql);
    $stmt->bind_param("i", $id);
    $stmt->execute();
    $result = $stmt->get_result();
    $fila = $result->fetch_assoc();

    echo "<input type='hidden' name='id' value='" . $fila['IDSugerencia'] . "'>";

    // Precargar los valores en las variables
    $usuario = $fila['Usuario'];
    $titulo = $fila['Titulo'];
    $descripcion = $fila['Descripcion'];
}

echo "<label for='usuario'>Usuario:</label><select name='usuario' required>";
while ($usuarioData = $usuarios->fetch_assoc()) {
    $selected = ($usuarioData['IDUsuario'] == $usuario) ? "selected" : "";
    echo "<option value='" . $usuarioData['IDUsuario'] . "' $selected>" . $usuarioData['Nombres'] . " " . $usuarioData['Apellidos'] . "</option>";
}
echo "</select><br>";

echo "<label for='titulo'>Título:</label><input type='text' name='titulo' value='" . htmlspecialchars($titulo) . "' placeholder='Título' required><br>";
echo "<label for='descripcion'>Descripción:</label><textarea name='descripcion' placeholder='Descripción' required>" . htmlspecialchars($descripcion) . "</textarea><br>";

if (isset($_GET['editar'])) {
    echo "<button type='submit' name='editar'>Actualizar Sugerencia</button>";
} else {
    echo "<button type='submit' name='crear'>Crear Sugerencia</button>";
}

echo "</form>";

// ****************************************************************************
// MOSTRAR LISTA DE SUGERENCIAS
// ****************************************************************************
if ($resultado->num_rows > 0) {
    echo "<h2>Lista de Sugerencias</h2>";
    echo "<table border='1'>";
    echo "<tr><th>ID</th><th>Usuario</th><th>Título</th><th>Descripción</th><th>Acciones</th></tr>";

    while ($fila = $resultado->fetch_assoc()) {
        echo "<tr>";
        echo "<td>" . $fila['IDSugerencia'] . "</td>";
        echo "<td>" . $fila['Nombres'] . " " . $fila['Apellidos'] . "</td>";
        echo "<td>" . $fila['Titulo'] . "</td>";
        echo "<td>" . $fila['Descripcion'] . "</td>";
        echo "<td>
                <a href='sugerencias.php?editar=" . $fila['IDSugerencia'] . "'>Editar</a> |
                <a href='sugerencias.php?eliminar=" . $fila['IDSugerencia'] . "' onclick='return confirm(\"¿Estás seguro de eliminar esta sugerencia?\");'>Eliminar</a>
              </td>";
        echo "</tr>";
    }
    echo "</table>";
} else {
    echo "<p>No hay sugerencias registradas.</p>";
}

// Cerrar la conexión
$conn->close();
?>