from typing import Dict

from trueskill import Rating, rate


def next_match(file_name: str):
    with open(file_name, "r") as f:
        lines = f.readlines()
        date, team1, team2 = None, None, None
        for line in lines:
            if line == "\n":
                continue
            if date is None:
                date = line.rstrip("\n")
            elif team1 is None:
                team1 = line.rstrip("\n").split(",")
                team1 = [player.strip() for player in team1]
            else:
                team2 = line.rstrip("\n").split(",")
                team2 = [player.strip() for player in team2]
                yield date, team1, team2
                date, team1, team2 = None, None, None


def main() -> None:
    ratings: Dict[str, Rating] = {}
    gen = next_match("results.txt")
    while True:
        try:
            date, team1, team2 = next(gen)
        except StopIteration:
            break
        for player in team1 + team2:
            if ratings.get(player) is None:
                ratings[player] = Rating()
        rating_t1 = [ratings[player] for player in team1]
        rating_t2 = [ratings[player] for player in team2]
        new_rating_t1, new_rating_t2 = rate([rating_t1, rating_t2], ranks=[0, 1])
        for i in range(len(new_rating_t1)):
            ratings[team1[i]] = new_rating_t1[i]
            ratings[team2[i]] = new_rating_t2[i]

    leaderboard = [
        (player, round(ratings[player].mu - 2 * ratings[player].sigma, 3))
        for player in ratings
    ]

    leaderboard.sort(key=lambda x: x[1], reverse=True)
    for player, rating in leaderboard:
        print(player, rating)


if __name__ == "__main__":
    main()
