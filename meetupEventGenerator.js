/*
 This is an goole sheet app script to interact with MeetUp API.
 The purpose of this script is to create/update the MeetUp event throught Google Sheet and MeetUp API.
 The original work is done by Yuren Ju (https://gist.github.com/yurenju/f104e154edd666566f1717a4230a1c7a#file-meetup-js-L62-L63)
 This is a modified version ,please feel free to contibute.
 */
 
//Define global variable across functions
var MEETUP_API_URI = '';
var MEETUP_API_KEY = '';


function create() {
  const MEETUP_SCHEDULE = 'Meetup Schedule';
  const TALKS = 'talks';
  const TITLE_INDEX = 2;
  const ABSTRACT_INDEX = 3;
  const SPEAKER_INDEX = 4;
  const SPEAKER_INTRO_INDEX = 5;
  const SLIDES_INDEX = 6;
  const LANGUAGE_INDEX = 7;
  const RECORD_INDEX = 8;
  const TIME_INDEX = 9;
  const OTHER_INDEX = 10;
  
  
  var ui = SpreadsheetApp.getUi();
  var sheet = SpreadsheetApp.getActiveSheet();
  var sheetName = sheet.getName();
  
  if (sheetName !== MEETUP_SCHEDULE) {
    ui.alert('Select a row in "Meetup Schedule" sheet to create an event', ui.ButtonSet.OK);
  } else {
    var talksSheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(TALKS);
    var rowIndex = SpreadsheetApp.getActiveRange().getRow();
    var values = sheet.getRange(rowIndex, 1, 1, 7).getValues()[0];
    Logger.log(values);
    var result = {
      date: values[0],
      start: values[1],
      end: values[2],
      schedule: []
    };
    values[6].split('\n').forEach(function (line) {
      line = line.trim();
      if (line.length === 0) {
        return;
      }
      
      var parts = line.split(' ');
      var time = parts[0];
      var slotInfo = parts[1];
      var slot = { time: time };
      if (slotInfo[0] === '#') {
        var talkRowIndex = parseInt(slotInfo.substr(1));
        var talkValues = talksSheet.getRange(talkRowIndex, 1, 1, 11).getValues()[0];
        slot.title = talkValues[TITLE_INDEX];
        slot.detail = {
          title: talkValues[TITLE_INDEX],
          abstract: talkValues[ABSTRACT_INDEX],
          speaker: talkValues[SPEAKER_INDEX],
          speakerIntro: talkValues[SPEAKER_INTRO_INDEX],
          slides: talkValues[SLIDES_INDEX],
          language: talkValues[LANGUAGE_INDEX],
          recordPreference: talkValues[RECORD_INDEX],
          timePreference: talkValues[TIME_INDEX],
          otherPreference: talkValues[OTHER_INDEX]
        };
      } else {
        slot.title = slotInfo;
      }
      result.schedule.push(slot);
    });
    ui.alert(JSON.stringify(result, null, 2), ui.ButtonSet.OK);
    createMeetup(result);
    Logger.log(JSON.stringify(result, null, 2));
  }
  
  
}

function createMeetup(payload) {
  var headers = {
    'x-api-key': MEETUP_API_KEY,
    'Content-Type': 'application/json'
  };
  var options = {
    'headers': headers,
    'method': 'post',
    'payload': JSON.stringify(payload)
  };
  
  var ui = SpreadsheetApp.getUi();
  var response = UrlFetchApp.fetch(MEETUP_API_URI, options);
  ui.alert(JSON.stringify(response), ui.ButtonSet.OK);
}

function update() {
  var ui = SpreadsheetApp.getUi();
  ui.alert(
     'Update an event',
      ui.ButtonSet.OK);
}

function onOpen(e) {
  var menu = SpreadsheetApp.getUi().createAddonMenu(); // Or DocumentApp or FormApp.
  menu.addItem('Create event', 'create');
  menu.addItem('Update event', 'update');
  menu.addToUi();
}
