'use strict'

const {PubSub} = require('@google-cloud/pubsub')

/**
 * Responds to any HTTP request.
 *
 * @param {!express:Request} req HTTP request context.
 * @param {!express:Response} res HTTP response context.
 */
exports.form = async(req, res) => {
  if (req.method === 'POST') {

    // Data to publish
    let message = JSON.stringify(req.body)

    // Send message
    try {
      
      const pubSubClient = new PubSub();
      const dataBuffer = Buffer.from(message);
      const customAttributes = {'timestamp': Date.now().toString()}
      const messageId = await pubSubClient
        .topic('form-submissions')
        .publish(dataBuffer, customAttributes)
      console.log(`Message ${messageId} published (${customAttributes["timestamp"]}).`)
      res.status(200).send(`POST: ${message} -> ${messageId}\n`)

    } catch(error) {
      console.error(new Error(`Backup json: ${message}`))
      console.error("Error publishing message to pubsub", error)
    }

  } else {
    res.status(200).send('GET: Hello World!')
  }
};
