let axios = require('axios');
let querystring = require('querystring');
let timestamp = require('unix-timestamp');

let apiKey = process.env.API_KEY;
let baseUrl = 'https://api.meetup.com/Taipei-Ethereum-Meetup';

function parseDesc(bodyData) {
    console.log('bodyData:',bodyData);
    let desc = '';
    let sche = bodyData.schedule;
    console.log('sche:',sche.length);
    for(let i = 0; i < sche.length; i++) {
        console.log('desc:',desc);
        let section = sche[i];
        desc = desc + 
        section.time + '<br>' +
        section.title + '<br>';
        if(section.detail) {
            desc = desc + 
            'by ' + section.detail.speaker + '<br>';   
        }
        desc = desc + '<br>';
    }
    console.log('desc all:',desc);
    return desc;
}

function newPostData(bodyData) {
    let name = bodyData.name || 'Monthly Meetup';
    let ts = timestamp.fromDate(bodyData.date)*1000; //in miliseconds
    let venueId = bodyData.venueId || 24798785;
    let desc = parseDesc(bodyData);
    
    return querystring.stringify({
        announce: false,
        name: name,
        description: desc,
        time: ts,
        publish_status: 'draft',
        venue_id: venueId
        //lat: 25.020000457763672,
        //lon: 121.44999694824219
    });
}

function newMeetup(bodyData ,callback) {
    let url = baseUrl + '/events' + '?key=' + apiKey;
    let axiosHeaders = {
        headers:{
            'Content-Type': 'application/x-www-form-urlencoded'
        }
    };
    axios.post(url,newPostData(bodyData),axiosHeaders)
    .then(res => {
        console.log('success:',res);
        callback(null,{
            statusCode: 200,
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(res.data)
        });
    })
    .catch(err => {
        console.log('err:',err);
        throw (err);
    }) ;
}

function updateMeetup(bodyData ,callback) {
    let eventId = bodyData.eventId;
    let url = baseUrl + '/events' + '/' + eventId + '?key=' + apiKey;
    let axiosHeaders = {
        headers:{
            'Content-Type': 'application/x-www-form-urlencoded'
        }
    };
    axios.patch(url,newPostData(bodyData),axiosHeaders)
    .then(res => {
        console.log('success:',res);
        callback(null,{
            statusCode: 200,
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(res.data)
        });
    })
    .catch(err => {
        console.log('err:',err);
        throw (err);
    }) ;
}

exports.handler = (event, context, callback) => {  
    try {
        let method = event.httpMethod;
        let bodyData = JSON.parse(event.body);
        if(method == 'POST') {
            newMeetup(bodyData ,callback);
        } else {
            updateMeetup(bodyData ,callback);
        }
        
    } catch (err) {
        callback(null,{
            statusCode: 400,
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({err:err})
        })
    }
};
