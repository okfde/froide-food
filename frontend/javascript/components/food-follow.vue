<template>
  <div v-if="!canFollow">
    <button v-if="follows" class="input-large btn btn-block btn-sm" :class="{'hover-btn-danger': !justFollowed}" @click.stop="unfollow">
      <span v-if="!justFollowed" class="on-hover">
        <i class="fa fa-remove" aria-hidden="true"></i>
        Anfrage entfolgen
      </span>
      <span :class="{'on-display': !justFollowed}">
        <i class="fa fa-star" aria-hidden="true"></i>
        Sie folgen dieser Anfrage!
      </span>
    </button>
    <button v-else class="input-large btn hover-btn-success btn-block btn-sm" @click.stop="doFollow">
      <span class="on-hover">
        <i class="fa fa-star" aria-hidden="true"></i>
        Anfrage folgen?
      </span>
      <span class="on-display">
        <i class="fa fa-star-o" aria-hidden="true"></i>
        Anfrage folgen?
      </span>
    </button>
  </div>
</template>

<script>

import {postData} from '../lib/utils.js'

export default {
  name: 'food-follow',
  props: {
    follow: {
      type: Object
    }
  },
  data () {
    return {
      working: false,
      justFollowed: false,
    }
  },
  computed: {
    canFollow () {
      return this.unknown || this.follow.canFollow
    },
    follows () {
      return this.unknown || this.follow.follows
    },
    unknown () {
      return this.follow === undefined
    },
    requestId () {
      let parts = this.follow.request.split('/')
      return parseInt(parts[parts.length - 2])
    }
  },
  methods: {
    doFollow () {
      this.justFollowed = true
      postData(
        '/api/v1/following/',
        {'request': this.requestId},
        this.$root.csrfToken
      ).then((data) => {
        this.$emit('followed', data['url'])
        window.setTimeout(() => this.justFollowed = false, 2000)
      })
    },
    unfollow () {
      if (this.justFollowed) {
        return
      }
      window.fetch(this.follow.resource_uri, {
        method: "DELETE",
        headers: {
          "Content-Type": "application/json",
          'X-CSRFToken': this.$root.csrfToken
        }
      }).then(() => {
        this.$emit('unfollowed')
      })
    }
  }
}
</script>
