; Instalador do Painel de Ocorrências (Inno Setup 6)
; Gerado por build.bat — não precisa abrir manualmente.

#define AppName "Painel de Ocorrências"
#define AppVersion "1.0.0"
#define AppExe "PainelOcorrencias.exe"

[Setup]
AppId={{6C1E4A52-7B0D-4F1B-9C3A-2E8F5D7A1B40}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher=TrackServices
DefaultDirName={localappdata}\Programs\PainelOcorrencias
DefaultGroupName={#AppName}
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
OutputDir=..\dist
OutputBaseFilename=Instalar-PainelOcorrencias
SetupIconFile=..\assets\trackservices.ico
UninstallDisplayIcon={app}\{#AppExe}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "pt"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"

[Tasks]
Name: "desktopicon"; Description: "Criar atalho na Área de Trabalho"; GroupDescription: "Atalhos:"

[Files]
Source: "..\dist\PainelOcorrencias\*"; DestDir: "{app}"; Flags: recursesubdirs ignoreversion

[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\{#AppExe}"
Name: "{group}\Desinstalar {#AppName}"; Filename: "{uninstallexe}"
Name: "{userdesktop}\{#AppName}"; Filename: "{app}\{#AppExe}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#AppExe}"; Description: "Abrir o {#AppName}"; Flags: nowait postinstall skipifsilent
