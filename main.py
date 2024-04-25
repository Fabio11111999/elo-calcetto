from elosports.elo import Elo
from collections import defaultdict
import plotly.express as px
import pandas
# import emoji


def read_file(file_name='results.txt'):
    with open(file_name) as f:
        lines = f.readlines()
        lines = [line.strip('\n') for line in lines if line != '\n']
        winners = [lines[i].replace(' ', '').split(',') for i in range(1, len(lines), 3)]
        losers = [lines[i].replace(' ', '').split(',') for i in range(2, len(lines), 3)]
        winners.reverse()
        losers.reverse()
        return winners, losers


def compute_win_rate(winners, losers):
    wins, matches = defaultdict(int), defaultdict(int)
    for team in winners:
        for player in team:
            wins[player] += 1
            matches[player] += 1
    for team in losers:
        for player in team:
            matches[player] += 1
    rates = [(round(100 / matches[p] * wins[p]), p) for p in matches.keys()]
    rates.sort(key=lambda x: -x[0])
    for percentage, player in rates:
        print(f'{player}: {wins[player]}/{matches[player] - wins[player]} ({percentage}%)')


def compute_streak(winners, losers):
    streak = defaultdict(int)
    for winning_team, losing_team in zip(winners, losers):
        for winner in winning_team:
            if streak[winner] >= 0:
                streak[winner] += 1
            else:
                streak[winner] = 1
        for loser in losing_team:
            if streak[loser] <= 0:
                streak[loser] -= 1
            else:
                streak[loser] = -1
    streak_list = list(streak.items())
    streak_list.sort(key=lambda x: -x[1])
    for player, count in streak_list:
        print(player + ': ' + abs(count) * ('\u2713' if count > 0 else 'x'))


def make_chart(history):
    players, matches, rating = [], [], []
    for i in range(len(history)):
        for player in history[i].keys():
            players.append(player)
            matches.append(i + 1)
            rating.append(history[i][player])
    df = pandas.DataFrame({'Player': players, 'Match': matches, 'Rating': rating})
    fig = px.line(df, x="Match", y="Rating", color='Player', markers=True)
    fig.show()


def update_rating(rating, winners, losers):
    league = Elo(k=200)
    rating_winner = 0
    rating_loser = 0
    for player in winners:
        rating_winner += rating[player]
    for player in losers:
        rating_loser += rating[player]
    differences = {}
    for winning_player in winners:
        winning_weighted_average = (rating_winner + 3 * rating[winning_player]) / 8
        losing_weighted_average = rating_loser / len(losers)
        league.addPlayer('Winner', winning_weighted_average)
        league.addPlayer('Loser', losing_weighted_average)
        league.gameOver(winner='Winner', loser='Loser', winnerHome=False)
        winner_difference = league.ratingDict['Winner'] - winning_weighted_average
        differences[winning_player] = winner_difference
    for losing_player in losers:
        winning_weighted_average = rating_winner / len(winners)
        losing_weighted_average = (rating_loser + (len(losers) - 2) * rating[losing_player]) / (len(losers) * 2 - 2)
        league.addPlayer('Winner', winning_weighted_average)
        league.addPlayer('Loser', losing_weighted_average)
        league.gameOver(winner='Winner', loser='Loser', winnerHome=False)
        loser_difference = league.ratingDict['Loser'] - losing_weighted_average
        differences[losing_player] = loser_difference
    for key in differences.keys():
        rating[key] += differences[key]


def main():
    winners, losers = read_file()
    compute_win_rate(winners, losers)
    compute_streak(winners, losers)
    rating = {}
    rating_history = []
    for team in winners:
        for player in team:
            rating[player] = 1500
    for team in losers:
        for player in team:
            rating[player] = 1500
    rating_history.append(rating.copy())
    for match in range(len(winners)):
        update_rating(rating, winners[match], losers[match])
        print(rating)
        rating_history.append(rating.copy())
    make_chart(rating_history)
    ordered_ratings = [(rating[player], player) for player in rating.keys()]
    ordered_ratings.sort(key=lambda x: -x[0])
    for i in range(len(ordered_ratings)):
        print(ordered_ratings[i][1], ordered_ratings[i][0])


if __name__ == '__main__':
    main()
