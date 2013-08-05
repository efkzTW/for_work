import sys

rom_rng = [1, 5, 10, 50, 100, 500, 1000]
int_to_rom = {1:'I',
			  5:'V',
			  10:'X',
			  50:'L',
			  100:'C',
			  500:'D',
			  1000:'M'}

def convert(num):
	roman_numeral = ""
	for i in range(1,len(rom_rng)+1):
		if i >= 5 and num == 9:
			roman_numeral += int_to_rom[1] + int_to_rom[10]
			return roman_numeral
		elif num // rom_rng[-i] == 4:
			roman_numeral += int_to_rom[rom_rng[-i]] + int_to_rom[rom_rng[-i+1]]
		elif rom_rng[-i]/10 > 0 and num // (rom_rng[-i]/10) == 9:
			roman_numeral += int_to_rom[rom_rng[-i-2]] + int_to_rom[rom_rng[-i]]
			num = num % (rom_rng[-i]/10)
		else:
			roman_numeral += int_to_rom[rom_rng[-i]] * (num // rom_rng[-i])
		num = num % rom_rng[-i]
	return roman_numeral

if __name__ == '__main__':
	print convert(int(sys.argv[1]))