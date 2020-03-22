'use strict'

const {PubSub} = require('@google-cloud/pubsub')
const formPage = process.env.FORM_PAGE
const successPage = process.env.SUCCESS_PAGE
const errorPage = process.env.ERROR_PAGE

/**
 * Responds to any HTTP request.
 *
 * @param {!express:Request} req HTTP request context.
 * @param {!express:Response} res HTTP response context.
 * 
 */
exports.form = async(req, res) => {
  if (req.method === 'POST') {

    // Data to publish
    let message = JSON.stringify(req.body)
    const timestamp = new Date().toISOString()
    const id = generateId()
    const customAttributes = {'timestamp': timestamp, 'id': id}
    console.log(`Backup json: ${message} / ${customAttributes}`)

    // Send message
    try {

      const dataBuffer = Buffer.from(message);
      const pubSubClient = new PubSub();
      const messageId = await pubSubClient
        .topic('form-submissions')
        .publish(dataBuffer, customAttributes)
      console.log(`Message ${messageId} published (${customAttributes}).`)
      console.log(`Redirecting to success page: ${successPage}`)
      res.redirect(`${successPage}?id=${id}`)

    } catch(error) {
      console.error("Error publishing message to pubsub", error)
      console.error(new Error(`Backup json: ${message} / `))
      console.log(`Redirecting to error page: ${errorPage}`)
      res.redirect(`${errorPage}?id=${id}`)
    }

  } else {
    // Bounce the user back to the form
    console.log("Redirecting back to form page.")
    res.redirect(formPage)
  }
};

function generateId() {
  // https://stackoverflow.com/questions/1349404/generate-random-string-characters-in-javascript
  const length = 8
  const characters = 'abcdefghijklmnopqrstuvwxyz0123456789';
  const charactersLength = characters.length;
  var result = '';
  for ( var i = 0; i < length; i++ ) {
     result += characters.charAt(Math.floor(Math.random() * charactersLength));
  }
  return result;
}
