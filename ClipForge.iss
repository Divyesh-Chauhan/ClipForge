; ClipForge Inno Setup Installer Script
; Clean and simple installer configuration

#define AppName "ClipForge"
#define AppVersion "1.0"
#define AppPublisher "CodeX"
#define AppExeName "ClipForge.exe"
#define BuildDir "dist"

[Setup]
AppId={{A1B2C3D4-E5F6-4A5B-8C9D-0E1F2A3B4C5D}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
DefaultDirName={autopf}\{#AppName}
DefaultGroupName={#AppName}
DisableProgramGroupPage=yes
LicenseFile=
OutputDir=.
OutputBaseFilename={#AppName}_Setup
; SetupIconFile - Comment out the line below if icon file is invalid or doesn't exist
; Uncomment the line below and ensure icon.ico exists and is valid:
;SetupIconFile=icon.ico
; Alternative: If icon is in assets folder: SetupIconFile=assets\clipforge.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "{#BuildDir}\ClipForge\{#AppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "{#BuildDir}\ClipForge\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\{#AppExeName}"
Name: "{group}\{cm:UninstallProgram},{#AppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#AppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(AppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Code]
// Wizard bitmap loading removed - ICO files cannot be loaded as bitmaps
// The SetupIconFile directive handles the installer icon properly
// No code needed here - installer will work fine without wizard bitmap

