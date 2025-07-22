rule pico {
	strings:
		$a = "llenge" wide ascii
		$b = {4d 5a 90 00}
		$c = "Startup" wide ascii
		$d = "IsDebuggerP" wide ascii
		$e = "LookupPriv" wide ascii
	condition:
		$a and $b and $c and $d and $e
}
