<template>
  <div class="card mt-3">
    <div class="card-header food-header">
      <label>
        Datum Kontrollbericht:
        <input type="date" v-model="reportdate" />
      </label>
      <button class="btn btn-danger" @click.prevent="addReport">
        Beanstandungen
      </button>
      <button class="btn btn-warning" @click.prevent="addReportDisgusting">
        Ekel-Alarm!
      </button>
      <button class="btn btn-success" @click.prevent="addReportNoComplains">
        Keine Beanstandungen
      </button>
    </div>
    <div class="card-body">
      <p v-if="dateList.length > 0">
        Gefundene Datumsangaben:
        <small v-for="d in dateList" :key="d"
          ><a @click.prevent="setDate(d)" href="#">{{ d }}</a
          >,
        </small>
      </p>
      <h4>
        <small>{{ date }}, {{ message.sender }}</small
        ><br />
        {{ message.subject }}
      </h4>
      <div class="content" @mouseup="checkSelection" ref="content">
        {{ message.content }}
      </div>
      <ul>
        <li v-for="att in attachmentList" :key="att.id">
          <a href="#" @click.prevent="loadAttachment(att)">
            {{ att.name }}
          </a>
        </li>
      </ul>
      <template v-if="attachment">
        <div class="mb-1">
          <a :href="attachment.site_url" target="_blank"
            >Im neuen Fenster öffnen</a
          >
          <a
            :href="attachmentRedactionUrl"
            target="_blank"
            class="btn btn-small btn-dark"
            >Schwärzen</a
          >
        </div>
        <div v-if="attachment.is_pdf" class="container-sm-full">
          <iframe
            :src="attachment.file_url"
            frameborder="0"
            style="width: 100%; height: 90vh; border: 0"></iframe>
        </div>
        <embed
          v-else
          :src="attachment.file_url"
          style="max-width: 100%"
          :type="attachment.filetype" />
      </template>
    </div>
  </div>
</template>

<script>
const DATE_RE = /(\d{1,2})\.(\d{1,2})(\.\d{2,4})?/g
const DATE_ONLY_RE = /^(\d{1,2})\.(\d{1,2})(?:\.(\d{2,4}))?$/

function isValidDate(d) {
  return d instanceof Date && !isNaN(d)
}

function leftpad(str) {
  str = '' + str
  const pad = '00'
  return pad.substring(0, pad.length - str.length) + str
}

function makeDate(str) {
  const match = DATE_ONLY_RE.exec(str)
  if (match === null) {
    return null
  }
  let year = match[3]
  if (!year) {
    year = 2019
  } else {
    year = parseInt(year, 10)
    if (year < 25) {
      year += 2000
    }
  }
  const d = new Date(year, parseInt(match[2], 10) - 1, parseInt(match[1], 10))
  if (!isValidDate(d)) {
    return null
  }
  return d
}

export default {
  name: 'food-report-message',
  mixins: [],
  components: {},
  props: {
    message: {
      type: Object
    },
    request: {
      type: Object
    }
  },
  mounted() {},
  data() {
    return {
      attachment: null,
      disgusting: false,
      complaints: false,
      reportdate: ''
    }
  },
  computed: {
    attachmentList() {
      return this.message.attachments.filter((att) => att.approved)
    },
    date() {
      let date = this.message.timestamp.split('T')[0].split('-')
      date.reverse()
      return date.join('.')
    },
    attachmentRedactionUrl() {
      return `/anfrage/${this.request.slug}/redact/${this.attachment.id}/`
    },
    dateList() {
      const already = {}
      const result = []
      let match
      do {
        match = DATE_RE.exec(this.message.content)
        if (match && already[match[0]] === undefined) {
          already[match[0]] = true
          result.push(match[0])
        }
      } while (match)
      return result
    }
  },
  methods: {
    loadAttachment(att) {
      this.attachment = att
    },
    addReport() {
      if (this.reportdate === '') {
        alert('Fehlendes Datum')
        return
      }
      this.complaints = true
      this.disgusting = false
      console.log(this.reportdate)
      this.emitReport()
    },
    addReportNoComplains() {
      if (this.reportdate === '') {
        alert('Fehlendes Datum')
        return
      }
      this.complaints = false
      this.disgusting = false
      console.log(this.reportdate)
      this.emitReport()
    },
    addReportDisgusting() {
      if (this.reportdate === '') {
        alert('Fehlendes Datum')
        return
      }
      this.complaints = true
      this.disgusting = true
      console.log(this.reportdate)
      this.emitReport()
    },
    emitReport() {
      this.$emit('addreport', {
        reportdate: this.reportdate,
        attachment: this.attachment ? this.attachment.id : null,
        message: this.message.id,
        complaints: this.complaints,
        disgusting: this.disgusting
      })
    },
    setDate(datestr) {
      let date = makeDate(datestr)
      if (date !== null) {
        this.reportdate = `${date.getFullYear()}-${leftpad(
          date.getMonth() + 1
        )}-${leftpad(date.getDate())}`
      }
    },
    checkSelection() {
      const selection = window.getSelection()
      const selectionRange = selection.getRangeAt(0)
      // startNode is the element that the selection starts in
      this.setDate(selection.toString())
    }
  }
}
</script>

<style lang="scss" scoped>
.content {
  white-space: pre-wrap;
  word-wrap: break-word;
}
.food-header {
  position: sticky;
  top: 0;
  background-color: #eee;
}
</style>
