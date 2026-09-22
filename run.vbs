Set shell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

root = fso.GetParentFolderName(WScript.ScriptFullName)
venvPython = root & "\.venv\Scripts\python.exe"
venvPythonw = root & "\.venv\Scripts\pythonw.exe"

If Not fso.FileExists(venvPython) Then
    MsgBox "No se encontro el entorno virtual." & vbCrLf & "Ejecuta install.bat primero.", vbExclamation, "Math Trainer"
    WScript.Quit 1
End If

If fso.FileExists(venvPythonw) Then
    runner = venvPythonw
Else
    runner = venvPython
End If

shell.Environment("Process")("PYTHONPATH") = root & "\src"
shell.Run """" & runner & """ -m math_trainer.main", 1, False
