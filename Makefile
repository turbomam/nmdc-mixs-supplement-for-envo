.PHONY: all clean

RUN=poetry run

all: clean target/nmdc-mixs-supplement-for-envo-merged-reduced-unmerged.ttl

clean:
	rm -rf target/*tsv
	rm -rf target/*ttl
	rm -rf target/*yaml

target/mixs_packages.tsv:
	curl -L -s 'https://docs.google.com/spreadsheets/d/1QDeeUcDqXes69Y2RjU2aWgOpCVWo5OVsBX9MKmMqi_o/export?format=tsv&gid=750683809' > $@

target/mixs_core.tsv:
	curl -L -s 'https://docs.google.com/spreadsheets/d/1QDeeUcDqXes69Y2RjU2aWgOpCVWo5OVsBX9MKmMqi_o/export?format=tsv&gid=178015749' > $@

target/envo.owl:
	curl -L -s 'http://purl.obolibrary.org/obo/envo.owl' > $@

target/nmdc-mixs-supplement-for-envo.ttl: target/mixs_packages.tsv target/mixs_core.tsv
	# todo add click CLI and class modeling?
	$(RUN) python nmdc-mixs-supplement-for-envo/classes-by-grid-expansion.py

target/nmdc-mixs-supplement-for-envo-merged.ttl: target/nmdc-mixs-supplement-for-envo.ttl target/envo.owl
	robot merge \
		--input $< \
		--input target/envo.owl \
		--collapse-import-closure false \
		--output $@

target/nmdc-mixs-supplement-for-envo-merged-reduced.ttl: target/nmdc-mixs-supplement-for-envo-merged.ttl
	# ELK or HermiT
	robot reduce \
		--input $< \
		--reasoner ELK \
		--very-verbose --output $@

target/nmdc-mixs-supplement-for-envo-merged-reduced-unmerged.ttl: target/nmdc-mixs-supplement-for-envo-merged-reduced.ttl target/envo.owl
	robot unmerge --input $< \
		--input target/envo.owl \
		--output $@


