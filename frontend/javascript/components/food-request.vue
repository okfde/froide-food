<template>
  <div class="container mb-5">
    <div class="row">
      <div class="col-12">
        <div v-if="fetching" class="loading">
          <food-loader></food-loader>
        </div>
        <template v-else>
          <div class="text-right">
            <button class="btn btn-sm btn-light" @click="$emit('close')">
              zurück
            </button>
          </div>
          <form method="post" :action="config.url.makeRequest" target="_blank">
            <input type="hidden" name="csrfmiddlewaretoken" :value="csrfToken"/>

            <input type="hidden" name="redirect_url" v-model="params.redirect"/>
            <input type="hidden" name="ref" v-model="params.ref"/>

            <input type="hidden" v-for="k in hideParams" :key="k" :name="k" value="1"/>
            
            <request-form v-if="!fetching"
              :publicbodies="publicbodies"
              :request-form="requestForm"
              :user="userInfo"
              :default-law="defaultLaw"
              :user-form="userForm"
              :initial-subject="subject"
              :initial-body="body"
              :show-draft="false"
              :hide-publicbody-chooser="true"
              :hide-full-text="true"
              :hide-editing="true"
              :law-type="lawType"
              :use-pseudonym="false"
              :config="config"
            ></request-form>
            <user-registration
              :form="userForm"
              :config="config"
              :user="userInfo"
              :default-law="defaultLaw"
              :address-help-text="addressHelpText"
            ></user-registration>
            <user-terms v-if="!userInfo"
              :form="userForm"
            ></user-terms>
            <div class="text-right">
              <button type="submit" class="btn btn-lg btn-success">
                <i class="fa fa-angle-double-right" aria-hidden="true"></i>
                Kontrollbericht anfragen
              </button>
            </div>
          </form>
        </template>
      </div>
    </div>
  </div>
</template>

<script>
import RequestForm from 'froide/frontend/javascript/components/request-form.vue'
import UserRegistration from 'froide/frontend/javascript/components/user-registration.vue'
import UserTerms from 'froide/frontend/javascript/components/user-terms.vue'
import {selectBestLaw} from 'froide/frontend/javascript/lib/law-select'

import FoodLoader from './food-loader'
import FoodDetailMixin from '../lib/detailmixin'

const LAW_TYPE = 'VIG'

export default {
  name: 'food-request',
  mixins: [FoodDetailMixin],
  components: {
    RequestForm,
    FoodLoader,
    UserTerms,
    UserRegistration
  },
  props: {
    data: {
      type: Object
    },
    config: {
      type: Object
    },
    requestForm: {
      type: Object
    },
    userInfo: {
      type: Object,
      default: null
    },
    userForm: {
      type: Object,
      default: null
    }
  },
  mounted () {
    if (!this.data.full) {
      this.getDetail(this.data)
    }
  },
  data () {
    return {
      fetching: !this.data.full,
      lawType: LAW_TYPE,
      addressHelpText: 'Ihre Adresse wird nicht öffentlich angezeigt. Im Anfragetext widersprechen Sie der Weitergabe Ihrer Anschrift an Dritte.'
    }
  },
  computed: {
    publicbodies () {
      return [this.data.publicbody]
    },
    publicBody () {
      return this.data.publicbody
    },
    params () {
      let params = {}
      if (!this.data.makeRequestURL) {
        return {}
      }
      this.data.makeRequestURL.split('?')[1].split('&').forEach((pair) => {
        pair = pair.split('=')
        params[pair[0]] = decodeURIComponent(pair[1])
      })
      return params
    },
    subject () {
      return this.params.subject || ''
    },
    body () {
      return this.params.body || ''
    },
    hideParams () {
      var a = []
      for (let k in this.params) {
        if (k.match(/hide_\w+/)) {
          a.push(k)
        }
      }
      return a
    },
    defaultLaw () {
      return selectBestLaw(this.publicBody.laws, LAW_TYPE)
    },
    csrfToken () {
      return document.querySelector('[name=csrfmiddlewaretoken]').value
    }
  },
  methods: {
    close () {
      this.$emit('close')
    }
  }
}
</script>


<style lang="scss" scoped>
  .loading {
    height: 100vh;
    padding-top: 30%;
    background-color: #ddd;
    animation: blinker 0.8s linear infinite;
    text-align: center;
  }

  .loading img {
    width: 10%;
  }

  @keyframes blinker {
    50% {
      opacity: 0.25;
    }
  }
</style>