<template>
  <li>
    <h5>
      Anfrage vom {{ requestDate }}
      <small class="ms-3">
        <a :href="request.url" target="_blank"> zur Anfrage&nbsp;&rarr; </a>
      </small>
    </h5>
    <p v-if="request.documents.length > 0">Dokumente in dieser Anfrage:</p>
    <ul v-if="request.documents.length > 0">
      <li v-for="doc in request.documents" :key="doc.url">
        <a :href="doc.url" target="_blank">
          {{ doc.name }}
        </a>
      </li>
    </ul>
    <p v-else class="text-muted">Noch keine Dokumente.</p>
  </li>
</template>

<script>
import { renderDate } from '../lib/utils'

export default {
  name: 'FoodDetailRequest',
  props: {
    request: {
      type: Object,
      required: true
    }
  },
  data() {
    return {
      fetching: false
    }
  },
  computed: {
    requestDate() {
      return renderDate(this.request.timestamp)
    }
  },
  watch: {
    data: function (data) {
      if (data && !data.full) {
        this.getDetail(data)
      }
    }
  }
}
</script>
