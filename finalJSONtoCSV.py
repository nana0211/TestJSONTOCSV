import json
import csv
import glob, os
from datetime import datetime
from dateutil import parser
import pandas as pd
outputFile = "pointing"

# folder of data
folder = "/Users/nana/Desktop/test_json/pointing"
#"D:/Users/isaaqi/Desktop/Giorgio Stuff/SPACE data"
#
# list of all the files
files = []
os.chdir(folder)
for a in glob.glob("*.json"):
    files.append(a)

# output columns
columnsBefore = ["Player_Name", "RotationTime", "MovementTime",
                "HomingTime_1", "HomingTime_2", "TotalHomingTime"]
columnsAfter = ["PointingJudgementTotalTime", "MapTotalTime", "CalculatedMapTotalTime","CalculatedMapTotalTimeSeconds", "MapRSq", "MemoryTotalTime", "CalculatedMemoryTotalTime","CalculatedMemoryTotalTimeSeconds", "MemoryPercentCorrect",
                "Overall_PerpectiveIdleTime", "Overall_PerspectiveTotalTime", "Overall_PerspectiveErrorMeasure","SPACEStartTime","SPACEEndTime", "SPACETotalTime"]

# output array used to hold data for output into csv file
outputArray = []
# maximum number of tasks/trials expected for certain items
totalPathIntegrationTrials = 13
totalPointingTasks = 6
totalPointingJudgements = 5
totalPerspectiveTakingTrials = 13

# Helper functions to get information from the json based on its structure
#region
# Egocentric Absolute Error from Pointing Judgement
# for every PointingJudgement in every PointingTask
def GetPointingJudgement_AbsoluteError(idata, i, j):
    if len(idata["Sessions"]["Egocentric"]) < 1:
        return ""
    temp = idata["Sessions"]["Egocentric"][0]["PointingTasks"]
    # if index i or j are out of bounds just return empty string
    if i >= len(temp):
        return ""
    temp = idata["Sessions"]["Egocentric"][0]["PointingTasks"][i]["PointingJudgements"]
    if j >= len(temp):
        return ""
    return idata["Sessions"]["Egocentric"][0]["PointingTasks"][i]["PointingJudgements"][j]["Absolute_Error"]
def GetPointingJudgement_CorrectAngle(idata, i, j):
    if len(idata["Sessions"]["Egocentric"]) < 1:
        return ""
    temp = idata["Sessions"]["Egocentric"][0]["PointingTasks"]
    # if index i or j are out of bounds just return empty string
    if i >= len(temp):
        return ""
    temp = idata["Sessions"]["Egocentric"][0]["PointingTasks"][i]["PointingJudgements"]
    if j >= len(temp):
        return ""
    return idata["Sessions"]["Egocentric"][0]["PointingTasks"][i]["PointingJudgements"][j]["Correct_Angle"]
def GetPointingJudgement_EstimatedAngle(idata, i, j):
    if len(idata["Sessions"]["Egocentric"]) < 1:
        return ""
    temp = idata["Sessions"]["Egocentric"][0]["PointingTasks"]
    # if index i or j are out of bounds just return empty string
    if i >= len(temp):
        return ""
    temp = idata["Sessions"]["Egocentric"][0]["PointingTasks"][i]["PointingJudgements"]
    if j >= len(temp):
        return ""
    return idata["Sessions"]["Egocentric"][0]["PointingTasks"][i]["PointingJudgements"][j]["Estimated_Angle"]
def GetPointingJudgement_RawError(idata, i, j):
    if len(idata["Sessions"]["Egocentric"]) < 1:
        return ""
    temp = idata["Sessions"]["Egocentric"][0]["PointingTasks"]
    # if index i or j are out of bounds just return empty string
    if i >= len(temp):
        return ""
    temp = idata["Sessions"]["Egocentric"][0]["PointingTasks"][i]["PointingJudgements"]
    if j >= len(temp):
        return ""
    return idata["Sessions"]["Egocentric"][0]["PointingTasks"][i]["PointingJudgements"][j]["Raw_Error"]
def GetPointingJudgement_CAMinusRE(idata,i,j):
    if len(idata["Sessions"]["Egocentric"]) < 1:
        return ""
    temp = idata["Sessions"]["Egocentric"][0]["PointingTasks"]
    # if index i or j are out of bounds just return empty string
    if i >= len(temp):
        return ""
    temp = idata["Sessions"]["Egocentric"][0]["PointingTasks"][i]["PointingJudgements"]
    if j >= len(temp):
        return ""
    cor_ang = float(idata["Sessions"]["Egocentric"][0]["PointingTasks"][i]["PointingJudgements"][j]["Correct_Angle"])
    est_ang = float(idata["Sessions"]["Egocentric"][0]["PointingTasks"][i]["PointingJudgements"][j]["Estimated_Angle"])
    return  cor_ang - est_ang 
def GetPointingJudgementTotalTime(idata):
    if len(idata["Sessions"]["Egocentric"]) < 1:
        return ""
    if len(idata["Sessions"]["Egocentric"][0]["PointingTasks"]) < 1:
        return ""
    lastPointingTask = len(idata["Sessions"]["Egocentric"][0]["PointingTasks"]) - 1
    if len(idata["Sessions"]["Egocentric"][0]["PointingTasks"][lastPointingTask]) < 1:
        return ""
    lastPointingJudgement = len(idata["Sessions"]["Egocentric"][0]["PointingTasks"][lastPointingTask]["PointingJudgements"]) - 1
    if len(idata["Sessions"]["Egocentric"][0]["PointingTasks"][lastPointingTask]) < 1:
        return ""
    lastRotation = len(idata["Sessions"]["Egocentric"][0]["PointingTasks"][lastPointingTask]["PointingJudgements"][lastPointingJudgement]["rawData"]["Rotations"]) - 1
    timeStart = parser.parse(idata["Sessions"]["Egocentric"][0]["PointingTasks"][0]["PointingJudgements"][0]["rawData"]["Rotations"][0]["timeStamp"])
    timeEnd = parser.parse(idata["Sessions"]["Egocentric"][0]["PointingTasks"][lastPointingTask]["PointingJudgements"][lastPointingJudgement]["rawData"]["Rotations"][lastRotation]["timeStamp"])
    return (timeEnd - timeStart).total_seconds()

# Get specific data from Path Integration
def GetPI_TotalTime(jsonData):
    return jsonData["totalTime"]
def GetPI_Distance(jsonData):
    return jsonData["PIDistance"]
def GetPI_DistRatio(jsonData):
    return jsonData["PIDistanceRatio"]
def GetPI_FinalAngle(jsonData):
    return jsonData["FinalPIAngle"]
def GetPIAngle(jsonData):
    return jsonData["PIAngle"]
def GetCorrectedPIAngle(jsonData):
    return jsonData["CorrectedPIAngle"]

# Get specific data from Perspective Taking
def GetPT_TotalTime(jsonData):
    return jsonData["TotalTime"]
def GetPT_IdleTime(jsonData):
    return jsonData["TotalIdleTime"]
def GetPT_FinalAngle(jsonData):
    return jsonData["FinalAngle"]
def GetPT_CorrectAngle(jsonData):
    return jsonData["CorrectAngle"]
def GetPT_DifferenceAngle(jsonData):
    return jsonData["DifferenceAngle"]
def GetPT_ErrorMeasure(jsonData):
    return jsonData["ErrorMeasure"]

# Functions to get simple items from the json
# (single items that are not from a list/array)
def GetPlayerName(idata):
    return idata["MetaData"]["Player_Name"]
def GetRotationTime(idata):
    if "Training" in idata.keys():
        return idata["Training"]["phase1"]["totalTime"]
    else:
        return ""
def GetMovementTime(idata):
    if "Training" in idata.keys():
        return idata["Training"]["phase2"]["totalTime"]
    else:
        return ""

def GetHomingTime1(idata):
    if "Training" in idata.keys():
        return idata["Training"]["phase5"]["Trials"][0]["Data"]["totalTime"]
    else:
        return ""

def GetHomingTime2(idata):
    if "Training" in idata.keys():
        return idata["Training"]["phase5"]["Trials"][1]["Data"]["totalTime"]
    else:
        return ""

def GetHomingTime3(idata):
    if "Training" in idata.keys():
            return idata["Training"]["phase5"]["Trials"][1]["Data"]["totalTime"] + idata["Training"]["phase5"]["Trials"][0]["Data"]["totalTime"]
    else:
        return ""
########################################################################
def GetMapTotalTime(idata):
    if len(idata["Sessions"]["Mapping"]) < 1:
        return ""
    return idata["Sessions"]["Mapping"][0]["TotalTime"]
def GetCalculatedMapTotalTime(idata):
    if len(idata["Sessions"]["Mapping"]) < 1:
        return ""
    timeStart = parser.parse(idata["Sessions"]["Mapping"][0]["StartTimeStamp"])
    timeEnd = parser.parse(idata["Sessions"]["Mapping"][0]["EndTimeStamp"])
    return (timeEnd - timeStart)
def GetCalculatedMapTotalTimeSeconds(idata):
    if len(idata["Sessions"]["Mapping"]) < 1:
        return ""
    timeStart = parser.parse(idata["Sessions"]["Mapping"][0]["StartTimeStamp"])
    timeEnd = parser.parse(idata["Sessions"]["Mapping"][0]["EndTimeStamp"])
    return (timeEnd - timeStart).total_seconds()
def GetMapRSq(idata):
    if len(idata["Sessions"]["Mapping"]) < 1:
        return ""
    return idata["Sessions"]["Mapping"][0]["BidimensionalRegression"]["Euclidean"]["R2"]
def GetMemoryTotalTime(idata):
    if len(idata["Sessions"]["Memory"]) < 1:
        return ""
    return idata["Sessions"]["Memory"][0]["TotalTime"]
def GetCalculatedMemoryTotalTime(idata):
    if len(idata["Sessions"]["Memory"]) < 1:
        return ""
    timeStart = parser.parse(idata["Sessions"]["Memory"][0]["StartTimeStamp"])
    timeEnd = parser.parse(idata["Sessions"]["Memory"][0]["EndTimeStamp"])
    return (timeEnd - timeStart)
def GetCalculatedMemoryTotalTimeSeconds(idata):
    if len(idata["Sessions"]["Memory"]) < 1:
        return ""
    timeStart = parser.parse(idata["Sessions"]["Memory"][0]["StartTimeStamp"])
    timeEnd = parser.parse(idata["Sessions"]["Memory"][0]["EndTimeStamp"])
    return (timeEnd - timeStart).total_seconds()
def GetMemoryPercentCorr(idata):
    if len(idata["Sessions"]["Memory"]) < 1:
        return ""
    return idata["Sessions"]["Memory"][0]["PercentCorrect"]
def GetPerspectiveTotalIdleTime(idata):
    if len(idata["Sessions"]["PerspectiveTaking"]) < 1:
        return ""
    return idata["Sessions"]["PerspectiveTaking"][0]["TotalIdleTime"]
def GetPerspectiveTotalTime(idata):
    if len(idata["Sessions"]["PerspectiveTaking"]) < 1:
        return ""
    return idata["Sessions"]["PerspectiveTaking"][0]["TotalTime"]
def GetPerspectiveError(idata):
    if len(idata["Sessions"]["PerspectiveTaking"]) < 1:
        return ""
    return idata["Sessions"]["PerspectiveTaking"][0]["AverageErrorMeasure"]
def GetCalculatedSPACEStartTime(idata):
    return idata["MetaData"]["Start_Timestamp"]
def GetCalculatedSPACEEndTime(idata):
    return idata["MetaData"]["End_Timestamp"]
def GetCalculatedSPACETotalTimeSeconds(idata):
    if(idata["MetaData"]["Start_Timestamp"] and idata["MetaData"]["End_Timestamp"]):
        timeStart = parser.parse(idata["MetaData"]["Start_Timestamp"])
        timeEnd = parser.parse(idata["MetaData"]["End_Timestamp"])
        return (timeEnd - timeStart).total_seconds()
    else:
        return ""
#endregion

# Add Columns for Path Integration trial data
for i in range (totalPathIntegrationTrials):
    columnsBefore.append("PI_TotalTime_" + str(i))
    columnsBefore.append("PI_Distance_" + str(i))
    columnsBefore.append("PI_DistRatio_" + str(i))
    columnsBefore.append("PI_FinalAngle_" + str(i))
    columnsBefore.append("PI_Angle_" + str(i))
    columnsBefore.append("Corrected_PI_Angle_" + str(i))
# Add columns for Pointing Judgement tasks
for i in range (totalPointingTasks):
    for j in range (totalPointingJudgements):
        columnsBefore.append("PointingJudgement_AbsoluteError_" + str(i) + "_Trial_" + str(j))
        #columnsBefore.append("PointingJudgement_CorrectAngle_" + str(i) + "_Trial_" + str(j))
        #columnsBefore.append("PointingJudgement_EstimatedAngle_" + str(i) + "_Trial_" + str(j))
        #columnsBefore.append("PointingJudgement_RawError_" + str(i) + "_Trial_" + str(j))
        #columnsBefore.append("PointingError_" + str(i) + "_Trial_" + str(j))

# Attach remaining column headers
for i in columnsAfter:
    columnsBefore.append(i)
# Add columns for Perspective Taking tasks
for i in range (totalPerspectiveTakingTrials):
    columnsBefore.append("PerspectiveTotalTime_" + str(i))
    columnsBefore.append("PerpectiveIdleTime_" + str(i))
    columnsBefore.append("PerpectiveFinalAngle_" + str(i))
    columnsBefore.append("PerpectiveCorrectAngle_" + str(i))
    columnsBefore.append("PerpectiveDifferenceAngle_" + str(i))
    columnsBefore.append("PerspectiveErrorMeasure_" + str(i))

# Attach first row of columns as headers
outputArray.append(columnsBefore)

# For every json file found
for f in files:
    outputLine = []
    # Open the file and load the data
    file = open(f)
    data = json.load(file)
    file.close()

    # Get first set of simple data
    outputLine.append(GetPlayerName(data))
    outputLine.append(GetRotationTime(data))
    outputLine.append(GetMovementTime(data))
    outputLine.append(GetHomingTime1(data))
    outputLine.append(GetHomingTime2(data))
    outputLine.append(GetHomingTime3(data))

    # Get Path Integration Data
    if len(data["Sessions"]["PathIntegration"]) > 0:
        for i in range(totalPathIntegrationTrials):
            temp = data["Sessions"]["PathIntegration"][0]["Trials"]
            if i >= len(temp):
                outputLine.append("")
                outputLine.append("")
                outputLine.append("")
                outputLine.append("")
                outputLine.append("")
                outputLine.append("")
            else:
                pit_data = data["Sessions"]["PathIntegration"][0]["Trials"][i]["Data"]
                outputLine.append(GetPI_TotalTime(pit_data))
                outputLine.append(GetPI_Distance(pit_data))
                outputLine.append(GetPI_DistRatio(pit_data))
                outputLine.append(GetPI_FinalAngle(pit_data))
                outputLine.append(GetPIAngle(pit_data))
                outputLine.append(GetCorrectedPIAngle(pit_data))
    else:
        for i in range(totalPathIntegrationTrials):
            outputLine.append("")
            outputLine.append("")
            outputLine.append("")
            outputLine.append("")
            outputLine.append("")
            outputLine.append("")
    # Get Pointing Judgements Data
    for i in range(totalPointingTasks):
        for j in range(totalPointingJudgements):
            cor_ang = GetPointingJudgement_CorrectAngle(data, i, j)
            raw_err = GetPointingJudgement_RawError(data, i, j)
            outputLine.append(GetPointingJudgement_AbsoluteError(data, i, j))
            #outputLine.append(cor_ang)
            #outputLine.append(GetPointingJudgement_EstimatedAngle(data,i,j))
            #outputLine.append(raw_err)
            #outputLine.append(GetPointingJudgement_CAMinusRE(data,i,j))

    # Get Remaining set of simple data
    outputLine.append(GetPointingJudgementTotalTime(data))
    outputLine.append(GetMapTotalTime(data))
    outputLine.append(GetCalculatedMapTotalTime(data))
    outputLine.append(GetCalculatedMapTotalTimeSeconds(data))
    outputLine.append(GetMapRSq(data))
    outputLine.append(GetMemoryTotalTime(data))
    outputLine.append(GetCalculatedMemoryTotalTime(data))
    outputLine.append(GetCalculatedMemoryTotalTimeSeconds(data))
    outputLine.append(GetMemoryPercentCorr(data))
    outputLine.append(GetPerspectiveTotalIdleTime(data))
    outputLine.append(GetPerspectiveTotalTime(data))
    outputLine.append(GetPerspectiveError(data))
    outputLine.append(GetCalculatedSPACEStartTime(data))
    outputLine.append(GetCalculatedSPACEEndTime(data))
    outputLine.append(GetCalculatedSPACETotalTimeSeconds(data))

    # Get Perspective Taking Data
    if len(data["Sessions"]["PerspectiveTaking"]) > 0:
        for i in range(totalPerspectiveTakingTrials):
            temp = data["Sessions"]["PerspectiveTaking"][0]["Trials"]
            # if no data, fill with empty string
            if i >= len(temp):
                outputLine.append("")
                outputLine.append("")
                outputLine.append("")
                outputLine.append("")
                outputLine.append("")
                outputLine.append("")
            else:
                # if yes data, get the data
                ptt_data = data["Sessions"]["PerspectiveTaking"][0]["Trials"][i]
                outputLine.append(GetPT_TotalTime(ptt_data))
                outputLine.append(GetPT_IdleTime(ptt_data))
                outputLine.append(GetPT_FinalAngle(ptt_data))
                outputLine.append(GetPT_CorrectAngle(ptt_data))
                outputLine.append(GetPT_DifferenceAngle(ptt_data))
                outputLine.append(GetPT_ErrorMeasure(ptt_data))
    else:
        # if no data, fill with empty string
        for i in range(totalPerspectiveTakingTrials):
            outputLine.append("")
            outputLine.append("")
            outputLine.append("")
            outputLine.append("")
            outputLine.append("")
            outputLine.append("")
    # Add participants data to final output
    outputArray.append(outputLine)
    print(outputArray)
outfilename = outputFile + "_1" + ".csv"
def JSONtoCSV(csv_file_path):
     # Convert the data array to a DataFrame
     df = pd.DataFrame(outputArray[1:], columns=outputArray[0])
    # Write the DataFrame to a CSV file
     df.to_csv(csv_file_path, index=False)

     return df
JSONtoCSV(outfilename)
    
# outfilename = outputFile + "_" + datetime.now().strftime("%d%m%Y_%H%M%S") + ".csv"
# with open(outfilename, 'a', newline='', encoding='utf-8') as output_file:
#    fileWriter = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
#    fileWriter.writerows(outputArray)
