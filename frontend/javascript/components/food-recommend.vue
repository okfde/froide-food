<template>
  <div>
    <div class="row justify-content-center mt-5">
      <div class="col-md-8">
        <h1 class="text-center">Einen Moment, {{ userName }}!</h1>

        <p class="lead">
          Sie haben in den letzten {{ days }}&nbsp;Tagen schon
          <strong>{{ requestCount }}&nbsp;Anfragen</strong> an die Behörde „{{
            publicbody.name
          }}“ gestellt.
        </p>

        <p>
          Es könnte sein, dass die Behörde Ihre Anfragen zu einer großen Anfrage
          zusammenfasst und für den erhöhten Aufwand
          <strong>Gebühren</strong> in Rechnung stellt.
        </p>

        <h3>Holen Sie sich Unterstützung!</h3>

        <p>
          Wir empfehlen Ihnen,
          <strong>eine Freundin oder einen Bekannten</strong> dazu zu bringen,
          die Anfrage bezüglich des Kontrollberichts für die Einrichtung „{{
            placeName
          }}“ zu stellen.
        </p>
      </div>
    </div>
    <div class="row justify-content-center">
      <div class="col mt-3 text-center">
        <a :href="smsLink" class="btn btn-primary">
          <span class="fa fa-comments-o" aria-hidden="true"></span>
          &nbsp;per Textnachricht
        </a>
      </div>

      <div class="col mt-3 text-center">
        <a :href="whatsAppLink" class="btn btn-success">
          <span class="fa fa-whatsapp" aria-hidden="true"></span>
          &nbsp;mit WhatsApp verschicken
        </a>
      </div>

      <div class="col mt-3 text-center">
        <a :href="mailLink" class="btn btn-secondary">
          <span class="fa fa-envelope" aria-hidden="true"></span>
          &nbsp;per Mail verschicken
        </a>
      </div>
    </div>
    <hr />

    <div class="row justify-content-center mt-5">
      <div class="col-md-8">
        <p>
          <button class="btn btn-secondary" @click="$emit('close')">
            zurück zur Karte
          </button>
        </p>
        <p>
          Sie wissen was Sie tun und möchten diese Anfrage dennoch stellen?
          <br />
          <button class="btn btn-sm btn-light mt-3" @click="close">
            Weiter zum Formular &rarr;
          </button>
        </p>
      </div>
    </div>
  </div>
</template>

<script>
const DAY_PERIOD = 90

export default {
  name: 'food-recommend',
  props: {
    requestCount: {
      type: Number
    },
    placeName: {
      type: String
    },
    publicbody: {
      type: Object
    },
    user: {
      type: Object
    },
    currentUrl: {
      type: String
    }
  },
  data() {
    return {
      days: DAY_PERIOD
    }
  },
  computed: {
    userName() {
      return `${this.user.first_name} ${this.user.last_name}`
    },
    socialUrl() {
      return this.currentUrl + '&social=1'
    },
    socialText() {
      return `Ich mache gerade bei einer Aktion zu Lebensmittelhygiene mit. Könntest du mir helfen und den Kontrollbericht von „${this.placeName}“ anfragen?\n\n${this.socialUrl}`
    },
    smsLink() {
      if (L.Browser.android) {
        return `sms://?body=${encodeURIComponent(this.socialText)}`
      }
      return `sms://&body=${encodeURIComponent(this.socialText)}`
    },
    whatsAppLink() {
      return `whatsapp://send?text=${encodeURIComponent(this.socialText)}`
    },
    mailLink() {
      let subject = encodeURIComponent(`Kontrollbericht ${this.placeName}`)
      return `mailto:?Subject=${subject}&Body=${encodeURIComponent(
        this.socialText
      )}`
    }
  },
  methods: {
    close() {
      this.$emit('close')
    }
  }
}
</script>
