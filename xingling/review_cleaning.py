# This file filter the original review json file from yelp dataset and form a clean
# json file with only the business_id and review text
import json

if __name__ == "__main__":
	f = open('yelp_academic_dataset_review.json','r')
	output = open('yelp_academic_dataset_review_cleaned.json','w')
	for line in f:
		inline = json.loads(line)
		outline = json.dumps({"business_id": inline['business_id'], "review": inline['text']})
		output.write(outline)
		output.write('\n')

	f.close()
	output.close()