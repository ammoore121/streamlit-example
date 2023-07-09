import streamlit as st
import pandas as pd
import requests
import datetime
import numpy as np
import uuid #note i have to use uuid here instead of shortuuid
# import matplotlib.pyplot as plt

#the app will reflect save and commits



st.title('Blue Dot :blue[Sports] :)') 




add_sidebar = st.sidebar.selectbox('Menu',('Place Bet','My Bets','My Bank','Test Env'))

if add_sidebar == "Test Env":
  df = pd.DataFrame({
  'first column': [1, 2, 3, 4],
  'second column': [10, 20, 30, 40]
})
  df
  st.line_chart(df)
  if st.button('See TN'):
     st.write("##:red[These Nuts]")
  else:
     st.write()
  
else:
  st.write()


if add_sidebar == "Place Bet":
     
     accountBalance = st.number_input('Insert Account Balance',value=5000)
     username = 'amoore'
     if st.button('Execute'):
        url = "https://content.unabated.com/markets/game-odds/v_gameodds.json"
          #Scrape MainLines from Unabated

        querystring = {"v":"23587068-b3e0-4152-99c1-b0bce9523702"}
        payload = ""
        r = requests.request("GET", url, data=payload, params=querystring)
        data = r.json()
        marketSources = (data["marketSources"])
        teams = (data["teams"])
        gameOddsEvents = (data["gameOddsEvents"])
        df_sportsbooks = pd.DataFrame(marketSources)
        df_teams = pd.DataFrame(teams)
        df_teams=df_teams.transpose()
        # create the GameOddsEvents Table. We do this one first to better reflect scrapeDate
        data = []
        for i in gameOddsEvents:
            for j in gameOddsEvents[i]:
                event_teams = j['eventTeams']
                #Sometimes id_1 does not have value of 1
                try:
                    id_0 = event_teams['0']['id']
                    if '1' in event_teams:
                        id_1 = event_teams['1']['id']                            
                        # Extract the americanPrice values from gameOddsMarketSourcesLines
                        game_odds_market_sources_lines = j['gameOddsMarketSourcesLines']
                        for market_source, market_data in game_odds_market_sources_lines.items():
                            siX= market_source
                            for bet_type, bet_data in market_data.items():
                                    american_price = bet_data['americanPrice']
                                    marketLineId= bet_data['marketLineId']
                                    marketId= bet_data['marketId']
                                    marketSourceId= bet_data['marketSourceId']
                                    points= bet_data['points']
                                    price= bet_data['price']
                                    sourcePrice= bet_data['sourcePrice']
                                    btX = bet_type
                                    # Store the extracted data in a tuple
                                    row = (i, j['eventId'],j['eventStart'],j['eventEnd'] ,id_0, id_1, siX, btX, marketLineId, marketSourceId,
                                    marketId, points,american_price, price, sourcePrice)
                                    data.append(row)
                except KeyError:
                    print("KeyError caught for event_teams:",event_teams)          
        # Create the DataFrame with the extracted data
        df_MainLineOdds = pd.DataFrame(data, columns=['lgX', 'eventId','eventStart','eventEnd','Teamid_0', 'Teamid_1', 'siX', 'btX', 'marketLineId','marketSourceId','marketId','points','american_price','price','sourcePrice'])
        df_MainLineOdds['lgX_league'] = df_MainLineOdds['lgX'].str.extract(r'lg([^:]+)')
        df_MainLineOdds['lgX_pt'] = df_MainLineOdds['lgX'].str.extract(r'pt([^:]+)')
        df_MainLineOdds['bet_stage'] = df_MainLineOdds['lgX'].apply(lambda x: x.split(':', 2)[2] if len(x.split(':', 2)) > 2 else np.nan)
        df_MainLineOdds['siX_side']= df_MainLineOdds['siX'].str.get(2)
        df_MainLineOdds['scrapeDateUTC'] = datetime.datetime.utcnow().isoformat()
        # ISO 8601 format for scrapedate is easiest to read in csv
        
        # Transforming the SportsBooks Reference Table
        # #Removing columns for building purposes#Note a bunch of other sportsbooks exist but are not shown on webpage. 
        df_sb = pd.DataFrame().assign(bookName=df_sportsbooks['name'],bookId=df_sportsbooks['id'],isActive=df_sportsbooks['isActive'],
        statusId=df_sportsbooks['statusId'],modifiedDate=df_sportsbooks['modifiedOn'])


        #Creating Binary flags 
        df_sb['nyBook']= 0
        df_sb['sharpBook']= 0


        #store binary flag reference
        df_nyBooks= pd.DataFrame(
            {"bookName" : ["Caesars", "DraftKings", "FanDuel", "FanDuel - Delayed", "BetMGM", "PointsBet", "BetRivers", "WynnBet", "Resorts", "BallyBet"],
            'nyBook': [1,1,1,1,1,1,1,1,1,1]
            }
        )
        df_sharpBooks = pd.DataFrame(
            {"bookName" :['Unabated','Pinnacle','Pinnacle - Delayed','Bookmaker','Prophet Exchange'],
            'sharpBook': [1,1,1,1,1]
            }
        )

        #Insert 1 if bookName matches the above
        df_sb=df_sb.set_index('bookName')
        df2 = df_nyBooks.set_index('bookName')
        df_sb.update(df2)

        df3=df_sharpBooks.set_index('bookName')
        df_sb.update(df3)

        #Move bookName back to a column
        # Step 1: Reset the index
        df_sb = df_sb.reset_index()

        # Step 2: Rename the 'index' column to 'ID'
        df_sb = df_sb.rename(columns={'index': 'ID'})

        # Step 3: Assign a new continuous integer index
        df_sb = df_sb.reset_index(drop=True)



        # Now we create the Teams table. 


        #slimming down df_teams
        df_teams_refined = pd.DataFrame().assign(teamId=df_teams['id'],teamName=df_teams['name'],abbreviation=df_teams['abbreviation'],
        eventId=df_teams['eventId'],sideId=df_teams['sideId'],leagueId=df_teams['leagueId'],divisionId=df_teams['divisionId'],
        modifiedDate=df_teams['modifiedOn'])


        #This is our Teams Table



        #manipulate the odds data

        #Define bet_type
        bet_type = {
            'bt1': 'Money_Line',
            'bt2':'Spread',
            'bt3': 'Total_Combined'}

        # Insert the bet_type & create filtered_df
        filtered_df = df_MainLineOdds[df_MainLineOdds['marketSourceId'].isin(df_sb['bookId'])].copy()
        filtered_df.loc[:, 'bet_type'] = filtered_df['btX'].map(bet_type)

        #Insert a league column
        league_dict = {
            '1':'NFL',
            '2':'CFB',
            '3':'NBA',
            '4':'NCAAB',
            '5':'MLB',
            '6':'NHL',
            '7':'WNBA'
            }

        filtered_df.loc[:,'league'] = filtered_df['lgX_league'].map(league_dict)

        # Insert the TeamNames and side(home/away) for Teamid_0 and Teamid_1
        # Merge the two dataframes on teamId
        filtered_df = df_teams_refined.merge(filtered_df, left_on='teamId', right_on='Teamid_0')

        # Rename the columns so they don't overwrite each other
        filtered_df = filtered_df.rename(columns={'teamName':'TeamName_0', 'abbreviation':'TeamAbbrev_0','sideId':'sideId_team0'})

        # Drop the now unnecessary merged columns column
        filtered_df = filtered_df.drop(columns={'teamId','TeamAbbrev_0','eventId_x','leagueId','divisionId','modifiedDate'})


        #repeat for Teamid_1
        filtered_df = filtered_df.merge(df_teams_refined, left_on='Teamid_1', right_on='teamId')
        filtered_df = filtered_df.rename(columns={'teamName':'TeamName_1', 'abbreviation':'TeamAbbrev_1','sideId':'sideId_team1'})
        filtered_df = filtered_df.drop(columns=['teamId','TeamAbbrev_1','leagueId','divisionId','modifiedDate','eventId'])
        filtered_df = filtered_df.rename(columns={'eventId_y' : 'eventId'})



        # Merge bookName into df_filtered
        filtered_df = filtered_df.merge(df_sb, left_on='marketSourceId', right_on='bookId')

        # Drop & rename columns. 

        filtered_df= filtered_df.drop(columns=['statusId','siX'])

        # Rename Columns 

        filtered_df= filtered_df.rename(columns={
            'isActive':'bookIsActive',
            'siX_side': 'bet_side'})


        #Insert betPeriod column

        ptX_definiton = {
            '1':'FullGame',
            '2':'Half_1',
            '3':'Half_2',
            '4':'Quarter_1',
            '5':'Quarter_2',
            '6':'Quarter_3',
            '7':'Quarter_4',
            '8':'Period_1',
            '9':'Period_2',
            '10':'Period_3'}


        filtered_df.loc[:, 'betPeriod'] = filtered_df['lgX_pt'].map(ptX_definiton)



        #Reorder to make it easier to read

        easiest_to_read_column_order = ['marketLineId','eventId', 'eventStart', 'eventEnd', 'modifiedDate', 'scrapeDateUTC', 'Teamid_0', 'TeamName_0', 'sideId_team0', 
        'Teamid_1', 'TeamName_1','sideId_team1', 'bet_side','lgX', 'lgX_league','league', 'lgX_pt','betPeriod', 'bet_stage',   
        'marketId', 'btX', 'bet_type', 'points', 'american_price', 
        'price', 'sourcePrice', 'ImpliedProb%','marketSourceId', 'bookName', 'bookId', 'bookIsActive', 'nyBook', 'sharpBook']

        filtered_df= filtered_df.reindex(columns=easiest_to_read_column_order)

        #bet_side as interger
        filtered_df["bet_side"] = filtered_df["bet_side"].astype(int)









        #remove games which occurred in the past. 
        filtered_df['eventStart'] = pd.to_datetime(filtered_df['eventStart'])
        filtered_df['scrapeDateUTC'] = pd.to_datetime(filtered_df['scrapeDateUTC'])

        # Create boolean mask
        mask = filtered_df["eventStart"] >= filtered_df["scrapeDateUTC"]

        filtered_df=filtered_df[mask]

        #record the source of the bet
        filtered_df['SourceName'] = "Unabated"


        #Insert a BetID  (short uuid) for each row

        bet_ids = [uuid.uuid4() for _ in range(len(filtered_df))]
        filtered_df.insert(0,'BetID',bet_ids)

        #Filtered_df is the raw unabated Odds. Save this
        

        SingleBets=pd.DataFrame()

        #rename columns to match master
        filtered_df = filtered_df.rename(columns={'TeamName_0':'AwayTeam','TeamName_1':'HomeTeam'})


        #change values of bet_side to reflect HomeTeam vs AwayTeam
        filtered_df['bet_side'] = filtered_df['bet_side'].replace({1: 'Home', 0: 'Away'})


        #remove bets with no american_price
        filtered_df= filtered_df.loc[filtered_df['american_price'] != 0]


        #input 0s for null values in points field (needed to ID tagging)
        filtered_df['points'] = filtered_df['points'].fillna(0)

        #rename eventStart to eventStartUTC
        filtered_df = filtered_df.rename(columns={'eventStart':'eventStartUTC'})


        SingleBets_append = filtered_df.loc[:,['BetID','eventId', 'eventStartUTC','scrapeDateUTC','bet_stage', 
                                        'league','AwayTeam','HomeTeam', 'bet_side',
                                        'betPeriod','bet_type','points', 'american_price',
                                        'bookName','nyBook','sharpBook', 'SourceName']]




        #add to single bets
        SingleBets = pd.concat([SingleBets,SingleBets_append], ignore_index=True)

        #add the OverUnderId

        def create_over_under_id(df):
            df['overUnderId'] = df['eventId'].astype(str) + df['eventStartUTC'].astype(str) + df['scrapeDateUTC'].astype(str) + \
                                df['bet_stage'] + df['HomeTeam'] + df['AwayTeam'] + df['league'] + df['betPeriod'] + \
                                df['bet_type'] +np.abs(df['points']).astype(str) + df['bookName'] + df['SourceName']
            return df

        SingleBets = create_over_under_id(SingleBets)





        # Check if there are only 2 records per overUnderId
        grouped = SingleBets.groupby('overUnderId').size()

        # Find groups with counts not equal to 2
        non_two_groups = grouped[grouped != 2]

        # Print non_two_groups
        print("Groups with counts not equal to 2:")
        print(non_two_groups)





        # Create a boolean mask for rows with overUnderId that are NOT in non_two_groups (i.e. overUnderId values that have exactly two records)
        mask = ~SingleBets['overUnderId'].isin(non_two_groups.index)

        # Apply the mask to keep only the rows with the overUnderId that are NOT in non_two_groups
        SingleBets = SingleBets[mask].reset_index(drop=True)




        #Add short uuid for betgroup. This will identify all records where equivalent values except BetID bookname american_price. This is done code side. Will make calculations easier

        def create_same_bet_id(df):
            df['sameBetId'] = df['eventStartUTC'].astype(str) + df['bet_stage'] + df['league']+ df['HomeTeam'] + df['AwayTeam'] + df['betPeriod'] + \
                                df['bet_type'] + np.abs(df['points']).astype(str) + df['bet_side'] 
            return df

        SingleBets = create_same_bet_id(SingleBets)
        

        #Get data ready for calculation input 
        #Group and Update Over/Under record into 1 row
        def group_and_update(df):
            group_cols = ['eventId', 'eventStartUTC','scrapeDateUTC','bet_stage',
            'HomeTeam', 'AwayTeam', 'league','betPeriod','bet_type','bookName','nyBook','sharpBook','SourceName','overUnderId']
            df0 = df.loc[df.bet_side == 'Home'].set_index(group_cols)
            df1 = df.loc[df.bet_side == 'Away'].set_index(group_cols)
            cols_to_rename = set(df1.columns) - set(group_cols)
            df1 = df1.rename(columns={col: col + "_2" for col in cols_to_rename})
            df0 = df0.join(df1)
            df0 = df0.reset_index()
            return df0

        #combined Rows (MasterData)
        calc_ready_df=group_and_update(SingleBets)




        # Define and Calulate metrics

        # American odds payout function
        ## takes in american odds and calculates the profit from the payout
        def calc_profit(american_odds):
            return american_odds / 100 if american_odds > 0  else 1 / ((-1 * american_odds) / 100)

        # Implied probability calculation
        ## takes in american odds and calculates an implied probability for 1 side
        def implied_prob(american_odds):
            return 100 / (american_odds + 100) if american_odds > 0 else (-1 * american_odds) / (-1 * american_odds + 100)

        # No-vig calculation
        def calc_no_vig(df, imp_prob_col_1, imp_prob_col_2):
            no_vig_1 = df[imp_prob_col_1].values / (df[imp_prob_col_1].values + df[imp_prob_col_2].values)
            no_vig_2 = df[imp_prob_col_2].values / (df[imp_prob_col_1].values + df[imp_prob_col_2].values)
            df['no_vig_1'] = no_vig_1
            df['no_vig_2'] = no_vig_2
            return df







        # Aggregate probability calculation
        def calc_agg_probability(df, novig_col_1, novig_col_2, groupby_cols):
            avg_prob = df.groupby(groupby_cols, as_index=False).agg({novig_col_1: 'mean', novig_col_2: 'mean'})
            avg_prob = avg_prob.rename(columns={novig_col_1: 'agg_prob_1', novig_col_2: 'agg_prob_2'})
            df = df.merge(avg_prob, on=groupby_cols, how='inner')
            return df

        def calc_expected_value(df):
            df['expected_val_1'] = (df['agg_prob_1'] * calc_profit(df['american_price'])) - (1 - df['agg_prob_1'])
            df['expected_val_2'] = (df['agg_prob_2'] * calc_profit(df['american_price_2'])) - (1 - df['agg_prob_2'])
            return df

        def calc_kelly_ratio(df):
            df['kelly_ratio_1'] = df['agg_prob_1'] - (1 - df['agg_prob_1']) / calc_profit(df['american_price'])
            df['kelly_ratio_2'] = df['agg_prob_2'] - (1 - df['agg_prob_2']) / calc_profit(df['american_price_2'])
            return df

        # Select output data and Drop NAs
        output_df = calc_ready_df.query('bet_stage == "pregame"').filter(['BetID','BetID_2','eventId', 'eventStartUTC','scrapeDateUTC','league' ,
        'HomeTeam', 'AwayTeam','bet_type', 'betPeriod', 'bookName','nyBook','SourceName', 'bet_side','points', 'american_price', 'overUnderId',  
        'sameBetId','sameBetId_2','bet_side_2','points_2', 'american_price_2'],axis=1).dropna(subset=['american_price', 'american_price_2'])

        # Implied probability
        output_df['imp_prob_1'] = output_df['american_price'].apply(implied_prob)
        output_df['imp_prob_2'] = output_df['american_price_2'].apply(implied_prob)
        # No-vig
        output_df = calc_no_vig(output_df, 'imp_prob_1', 'imp_prob_2')
        # Avg probability
        output_df = calc_agg_probability(output_df, 'no_vig_1', 'no_vig_2', ['eventId', 'bet_type', 'betPeriod', 'points'])
        # Expected value
        output_df = output_df.apply(calc_expected_value, axis=1)
        # Kelly ratio
        output_df = output_df.apply(calc_kelly_ratio, axis=1)
        # Sort dataframe by largest value between expected_val_1 and expected_val_2
        output_df['temp_col'] = np.where(output_df['expected_val_1'] > output_df['expected_val_2'], output_df['expected_val_1'], output_df['expected_val_2'])
        output_df = output_df.sort_values(by='temp_col', ascending=False)
        output_df = output_df.drop('temp_col', axis=1)


        # Kelly Allocations
        #Create Kelly allocated betsizes

        output_df['betSize_k75_1'] = (output_df['kelly_ratio_1']*.75) * accountBalance
        output_df['betSize_k75_2'] = (output_df['kelly_ratio_2']*.75) * accountBalance

        output_df['betSize_k50_1'] = (output_df['kelly_ratio_1']*.50) * accountBalance
        output_df['betSize_k50_2'] = (output_df['kelly_ratio_2']*.50) * accountBalance

        output_df['betSize_k25_1'] = (output_df['kelly_ratio_1']*.25) * accountBalance
        output_df['betSize_k25_2'] = (output_df['kelly_ratio_2']*.25) * accountBalance

        output_df['betSize_k15_1'] = (output_df['kelly_ratio_1']*.15) * accountBalance
        output_df['betSize_k15_2'] = (output_df['kelly_ratio_2']*.15) * accountBalance


        # Separate 1 row into 2 so we can filter by EV per unique bet

        # I want to split the records and capture the individual settings odds in a new row with the same shared elements. 
        # I want to standardize the field naming





        # Split data frame into two based on section 1 and section 2 
        df1 = output_df.copy()
        df1 = df1[[
        'BetID',
        'eventId',
        'eventStartUTC',
        'scrapeDateUTC',
        'league',
        'HomeTeam',
        'AwayTeam',
        'bet_type',
        'betPeriod',
        'bookName',
        'nyBook',
        'bet_side',
        'points',
        'american_price',
        'overUnderId',
        'sameBetId',
        'imp_prob_1',
        'no_vig_1',
        'agg_prob_1',
        'expected_val_1',
        'kelly_ratio_1',
        'betSize_k75_1',
        'betSize_k50_1',
        'betSize_k25_1',
        'betSize_k15_1',
        'SourceName']]

        df2= output_df.copy()
        df2 = df2[[
        'BetID_2',
        'eventId',
        'eventStartUTC',
        'scrapeDateUTC',
        'league',
        'HomeTeam',
        'AwayTeam',
        'bet_type',
        'betPeriod',
        'bookName',
        'nyBook',
        'bet_side_2', 
        'points_2',
        'american_price_2',
        'overUnderId',
        'sameBetId_2',
        'imp_prob_2',
        'no_vig_2',
        'agg_prob_2',
        'expected_val_2',
        'kelly_ratio_2',
        'betSize_k75_2',
        'betSize_k50_2',
        'betSize_k25_2',
        'betSize_k15_2',
        'SourceName']]

        # Rename columns in df1 and df2
        df1.rename(columns={
        'bet_side': 'bet_side',
        'points': 'points',
        'american_price': 'american_price',
        'imp_prob_1': 'imp_prob',
        'no_vig_1': 'no_vig',
        'agg_prob_1': 'agg_prob',
        'expected_val_1': 'expected_val',
        'kelly_ratio_1': 'kelly_ratio',
        'betSize_k75_1': 'betSize_k75',
        'betSize_k50_1': 'betSize_k50',
        'betSize_k25_1': 'betSize_k25',
        'betSize_k15_1': 'betSize_k15'}, inplace=True)

        df2.rename(columns={
        'BetID_2':'BetID',
        'bet_side_2': 'bet_side',
        'points_2': 'points',
        'american_price_2': 'american_price',
        'sameBetId_2' : 'sameBetId',
        'imp_prob_2': 'imp_prob',
        'no_vig_2': 'no_vig',
        'agg_prob_2': 'agg_prob',
        'expected_val_2': 'expected_val',
        'kelly_ratio_2': 'kelly_ratio',
        'betSize_k75_2': 'betSize_k75',
        'betSize_k50_2': 'betSize_k50',
        'betSize_k25_2': 'betSize_k25',
        'betSize_k15_2': 'betSize_k15'}, inplace=True)

        #create new df_merged cocatinating both dfs vertically(rows)
        Calculations_df = pd.concat([df1,df2], axis=0)


        #filter by Largest->Smalled EV
        Calculations_df.sort_values(by='expected_val', ascending=False, inplace=True)
        

        Calculations_df=Calculations_df.copy()
        st.write("Calculations_df- this is the full calculated data")
        Calculations_df

        #Limit bets to NY books

        NYoutput_df = Calculations_df[Calculations_df['nyBook']==1]


        #Add an index to later input bets taken 
        NYoutput_df['inputIndex'] = range(1,len(NYoutput_df)+1)

        # #Record the physical location the bet was placed
        # NYoutput_df['PlacedIn'] = 'NY'

        #select columns to display
        NYoutput_df1 = NYoutput_df[['inputIndex','eventStartUTC','league','AwayTeam','HomeTeam','bet_type','betPeriod', 'bookName', 'bet_side'
                    ,'points','american_price','expected_val','betSize_k25',]].head(60)
        st.write("NY state bets filtered by EV")
        st.dataframe(NYoutput_df1, width=5000)
        
        #Chart Bet Group Sizes by sameBetId
        # Group by sameBetId and count the size of each group
        grouped_by_sameBetId = SingleBets.groupby('sameBetId').size()

        # # Plot the histogram

        # plt.hist(grouped_by_sameBetId, bins=range(1, grouped_by_sameBetId.max() + 2), align='left', rwidth=0.8)
        # plt.xlabel('Group Size')
        # plt.ylabel('# of bets with X number Groupsize')
        # plt.title('Bet Group Sizes by sameBetId')

        # st.pyplot(plt)

     else:
          st.write()