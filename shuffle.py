from random import shuffle


if __name__ == "__main__":
    with open("participants.tsv") as f:
        lines = f.readlines()
        lines = [line.split('\t') for line in lines]
        headers = lines[0]
        # 0:id
        # 1:competitor.name
        # 2:competitor.school.externalId
        # 3:competitor.school.name
        # 4:competitor.school.location.city.name
        # 5:competitor.school.location.city.province.id
        # 6:member.name
        # 7:member.surname
        lines = lines[1:]
        ids = [line[0] for line in lines]
        schools = [line[2] for line in lines]
        school_names = [line[3] for line in lines]
        cities = [line[4] for line in lines]
        provinces = [line[5] for line in lines]
        names = [line[6] for line in lines]
        surnames = [line[7].strip() for line in lines]

        shuffle(surnames)
        shuffle(names)
        shuffle(ids)

        lines = zip(ids,names,surnames,schools,school_names,cities,provinces)
        for line in lines:
            print("\t".join(line))
        