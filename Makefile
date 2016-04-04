# Definitions

# Steps (must use tabs)
all: test

test:
	mkdir test_output
	./trimVarscan.py -t test_input/target.bed -l test_input/cnv.files -m test_output/markers.txt -s test_output/segments.txt
	diff test_output/markers.txt expected_output/markers.txt
	diff test_output/segments.txt expected_output/segments.txt
	./trimZygosity.py -l test_input/zyg.files -m test_output/zyg.markers -s test_output/zyg.segments
	diff test_output/zyg.markers expected_output/zyg.markers
	diff test_output/zyg.segments expected_output/zyg.segments
