'use strict'

const {PubSub} = require('@google-cloud/pubsub')

/**
 * Responds to any HTTP request.
 *
 * @param {!express:Request} req HTTP request context.
 * @param {!express:Response} res HTTP response context.
 */
exports.form = (req, res) => {
  if (req.method === 'POST') {

    // Data to publish
    let message = JSON.stringify(req.body)

    // Send message
    // TODO dump to the console in case of error
    const pubSubClient = new PubSub();
    const dataBuffer = Buffer.from(message);
    const customAttributes = {'timestamp': Date.now()}
    const messageId = pubSubClient
      .topic('form-submissions')
      .publish(dataBuffer, customAttributes)
    console.log(`Message ${messageId} published.`)
    res.status(200).send(`POST: ${message} -> ${messageId}\n`)
  } else {
    res.status(200).send('GET: Hello World!')
  }
};
