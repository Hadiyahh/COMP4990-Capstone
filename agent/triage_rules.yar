import "math"

// nothing = 0 hits
// deep scan = 1 to 3 hits (sneaky)
// normal scan = 4+ hits or the definitive rule (super noisy)

rule Triage_Networking_Capability {
    meta:
        description = "Detects netowrk stuff"
        author = "Group 29"
    strings:
        // common net libs we see in the labs
        $lib1 = "wininet.dll" ascii wide nocase
        $lib2 = "winhttp.dll" ascii wide nocase
        $lib3 = "ws2_32.dll" ascii wide nocase
        
        $proto1 = "http://" ascii wide
        $proto2 = "https://" ascii wide
        $proto3 = "ftp://" ascii wide
        
        // weird api calls for calling out
        $api1 = "InternetOpen" ascii wide
        $api2 = "HttpSendRequest" ascii wide
        $api3 = "gethostbyname" ascii wide
    condition:
        any of ($lib*) and (any of ($proto*) or any of ($api*))
}

rule Triage_Process_Injection {
    meta:
        description = "Detects injection apis"
        author = "Group 29"
    strings:
        // mem alloc stuff, kinda sus for injection
        $api1 = "VirtualAllocEx" ascii wide
        $api2 = "WriteProcessMemory" ascii wide
        $api3 = "CreateRemoteThread" ascii wide
        $api4 = "NtCreateThreadEx" ascii wide
        $api5 = "SetThreadContext" ascii wide
    condition:
        2 of them
}

rule Triage_High_Entropy_Packed {
    meta:
        description = "Detects packed files"
        author = "Group 29"
    condition:
        // chk if file is big enough and entropy is high, meaning its definitly packed
        filesize > 50KB and math.entropy(0, filesize) > 7.2
}

rule Triage_Sandbox_Evasion {
    meta:
        description = "Detects if its trying to hide from VMs"
        author = "Group 29"
    strings:
        // checking for vmware or virtualbox processes
        $vm1 = "VBoxService.exe" ascii wide nocase
        $vm2 = "vmtoolsd.exe" ascii wide nocase
        $vm3 = "qemu-ga.exe" ascii wide nocase
    condition:
        any of them
}

rule Triage_Anti_Debugging {
    meta:
        description = "Checks if its looking for debuggers"
        author = "Group 29"
    strings:
        // tries to stop us from reversing it
        $dbg1 = "IsDebuggerPresent" ascii wide
        $dbg2 = "CheckRemoteDebuggerPresent" ascii wide
        $dbg3 = "OutputDebugString" ascii wide
    condition:
        2 of them
}

rule Triage_Persistence {
    meta:
        description = "Detects run keys for persistance"
        author = "Group 29"
    strings:
        // tries to start up automaticly
        $reg1 = "Software\\Microsoft\\Windows\\CurrentVersion\\Run" ascii wide nocase
        $reg2 = "Software\\Microsoft\\Windows\\CurrentVersion\\RunOnce" ascii wide nocase
        $reg3 = "Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\Explorer\\Run" ascii wide nocase
    condition:
        any of them
}

rule Triage_Crypto_Ransom_Stuff {
    meta:
        description = "Checks if it loads crypto libaries for ransomeware"
        author = "Group 29"
    strings:
        // apis used to encrypt files 
        $crypt1 = "CryptAcquireContext" ascii wide
        $crypt2 = "CryptEncrypt" ascii wide
        $crypt3 = "ADVAPI32.dll" ascii wide nocase
    condition:
        2 of them
}

rule Triage_System_Discovery {
    meta:
        description = "Checks if its looking around the computer"
        author = "Group 29"
    strings:
        // malware always tries to find out where it landed
        $disc1 = "GetLogicalDrives" ascii wide
        $disc2 = "GetComputerName" ascii wide
        $disc3 = "EnumProcesses" ascii wide
    condition:
        2 of them
}

rule Triage_Suspicious_Downloader {
    meta:
        description = "Detects powershell or scripts trying to download stage 2"
        author = "Group 29"
    strings:
        // built in windows tools getting abused
        $ps1 = "Net.WebClient" ascii wide nocase
        $ps2 = "DownloadString" ascii wide nocase
        $bits = "bitsadmin /transfer" ascii wide nocase
        $cert = "certutil.exe -urlcache -split -f" ascii wide nocase
    condition:
        any of them
}

rule Triage_Keylogging_APIs {
    meta:
        description = "Checks for apis that record keystrokes"
        author = "Group 29"
    strings:
        // super common for spyeware
        $key1 = "GetAsyncKeyState" ascii wide
        $key2 = "SetWindowsHookEx" ascii wide
        $key3 = "GetKeyboardState" ascii wide
    condition:
        2 of them
}

rule Triage_Credential_Dumping {
    meta:
        description = "Detects stuff trying to steal passwords from memory"
        author = "Group 29"
    strings:
        // looking for lsass or using mimikatz style tricks
        $dump1 = "lsass.exe" ascii wide nocase
        $dump2 = "SeDebugPrivilege" ascii wide nocase
        $dump3 = "MiniDumpWriteDump" ascii wide
    condition:
        2 of them
}

rule Triage_Suspicious_Macro_Strings {
    meta:
        description = "Office docs running weird macros"
        author = "Group 29"
    strings:
        // macro auto executing
        $mac1 = "AutoOpen" ascii wide nocase
        $mac2 = "Document_Open" ascii wide nocase
        $mac3 = "Workbook_Open" ascii wide nocase
        $mac4 = "Shell(" ascii wide nocase
    condition:
        2 of them
}

rule Triage_Privilege_Escalation {
    meta:
        description = "Trying to get admin rights"
        author = "Group 29"
    strings:
        // adjusting tokens to get system level access
        $priv1 = "AdjustTokenPrivileges" ascii wide
        $priv2 = "LookupPrivilegeValue" ascii wide
        $priv3 = "OpenProcessToken" ascii wide
    condition:
        all of them
}

rule Triage_WMI_Query_Usage {
    meta:
        description = "Abusing WMI to run commands"
        author = "Group 29"
    strings:
        // wmi is used alot by fileless malware
        $wmi1 = "ExecQuery" ascii wide
        $wmi2 = "Win32_Process" ascii wide
        $wmi3 = "ROOT\\CIMV2" ascii wide nocase
    condition:
        2 of them
}

rule Definitive_Malware_Signature {
    meta:
        description = "Known bad strings for the normal scan bucket"
        author = "Group 29"
    strings:
        // straight up malware strings, we know its bad if this hits
        // since we got rid of quick scan, this just goes to normal scan now
        $s1 = "nc -e /bin/sh" ascii nocase
        $s2 = "files have been encrypted" ascii wide nocase
        $s3 = "vssadmin.exe Delete Shadows /All /Quiet" ascii wide nocase
        $s4 = "Mimikatz" ascii wide nocase
        $s5 = "WannaDecryptor" ascii wide nocase
    condition:
        any of them
}