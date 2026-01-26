<template>
  <div class="container mb-5">
    <div class="row">
      <div class="col-12">
        <div v-if="fetching" class="loading">
          <FoodLoader></FoodLoader>
        </div>
        <template v-else>
          <div class="text-end">
            <button class="btn btn-sm btn-light" @click="$emit('close')">
              zurück
            </button>
          </div>
          <template v-if="data.authority_cooperative">
            <h3>{{ data.authority_title }}</h3>
            <div class="fake-markdown" v-html="authorityDescriptionHtml"></div>
            <p class="mt-5">
              <button class="btn btn-light" @click="$emit('close')">
                zurück zur Karte
              </button>
            </p>
          </template>
          <FoodRecommend
            v-else-if="showWarning"
            :user="userInfo"
            :publicbody="publicBody"
            :place-name="data.name"
            :request-count="userRequestCount"
            :current-url="currentUrl"
            @close="closedWarning = true" />
          <template v-else-if="!canRequest">
            <p>Dieser Betrieb wurde zwischenzeitlich schon angefragt.</p>
            <button class="btn btn-secondary" @click="$emit('close')">
              zurück
            </button>
          </template>
          <form
            v-else
            method="post"
            @submit="formSubmit"
            :action="config.url.makeRequest"
            target="_blank">
            <input
              type="hidden"
              name="csrfmiddlewaretoken"
              :value="csrfToken" />

            <input
              type="hidden"
              name="redirect_url"
              v-model="params.redirect" />
            <input type="hidden" name="reference" v-model="params.ref" />
            <input type="hidden" name="public" value="True" />
            <input
              type="hidden"
              v-for="k in hideParams"
              :key="k"
              :name="k"
              value="1" />
            <div class="mt-5" v-if="!fetching && publicBody">
              <div class="fs-3">
                An: {{ publicBody.name }}
                <a :href="publicBody.site_url" target="_blank">
                  <span class="fa fa-info-circle" />
                </a>
              </div>
              <div
                v-if="defaultLaw?.request_note_html"
                class="alert alert-warning my-2"
                v-html="defaultLaw.request_note_html"
                />
              <div
                v-if="publicBody?.request_note_html"
                class="alert alert-warning my-2"
                v-html="publicBody.request_note_html"
                />
            </div>
            <RequestForm
              v-if="!fetching"
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
              :config="config"></RequestForm>
            <div class="card mb-3">
              <div class="card-body">
                <UserCreateAccount
                  v-if="!userInfo"
                  :config="config"
                  :request-form="requestForm"
                  :user-form="userForm"
                  :default-law="defaultLaw"
                  :address-help-text="addressHelpText"
                  :address-required="true"
                  >
                  <template #userPublicPreamble>
                    <span v-html="userForm.fields.private?.help_text" />
                  </template>
                </UserCreateAccount>
                <UserConfirmation
                  :form="userForm"
                  />
              </div>
            </div>
            <p v-if="!userInfo" class="small text-end">
              Sie erhalten im Rahmen der Aktion „Topf Secret“ einmalig eine
              separate E-Mail von foodwatch. (<a
                href="https://www.foodwatch.org/de/datenschutz/#topfsecret"
                >Datenschutz</a
              >)
            </p>
            <div class="text-end">
              <button
                type="submit"
                class="btn btn-lg btn-success"
                :disabled="submitting">
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
import RequestForm from '~froide/frontend/javascript/components/makerequest/request-form.vue'
import StoreValueMixin from 'froide/frontend/javascript/components/makerequest/lib/store-values-mixin'
import UserCreateAccount from 'froide/frontend/javascript/components/makerequest/user-create-account.vue'
import UserConfirmation from 'froide/frontend/javascript/components/makerequest/user-confirmation.vue'
import { selectBestLaw } from '~froide/frontend/javascript/lib/law-select'

import FoodDetailMixin from '../lib/detailmixin'
import FoodItemMixin from '../lib/mixin.js'
import FoodLoader from './food-loader'
import FoodRecommend from './food-recommend'

const MAX_REQUEST_COUNT = 3
const LAW_TYPE = 'VIG'

export default {
  name: 'FoodRequest',
  mixins: [FoodDetailMixin, FoodItemMixin, StoreValueMixin],
  components: {
    RequestForm,
    FoodLoader,
    FoodRecommend,
    UserCreateAccount,
    UserConfirmation
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
    },
    currentUrl: {
      type: String
    }
  },
  mounted() {
    if (!this.data.full) {
      this.getDetail(this.data)
    }
  },
  data() {
    return {
      pbScope: 'food-',
      fetching: !this.data.full,
      lawType: LAW_TYPE,
      closedWarning: false,
      submitting: false,
      addressHelpText:
        'Ihre Adresse wird nicht öffentlich angezeigt. <strong class="text-danger">Es kann passieren, dass die zuständige Behörde auf Nachfrage des Betriebs Ihren Namen und Ihre Anschrift an den Betrieb weiterleitet.</strong>'
    }
  },
  created() {
    this.initAllStoreValues()
  },
  computed: {
    csrfToken() {
      return this.$root.csrfToken
    },
    publicbodies() {
      return [this.data.publicbody]
    },
    publicBody() {
      return this.data.publicbody
    },
    showWarning() {
      return (
        this.userInfo &&
        this.data.userRequestCount >= MAX_REQUEST_COUNT &&
        !this.closedWarning
      )
    },
    userRequestCount() {
      return this.data.userRequestCount
    },
    params() {
      const params = {}
      if (!this.data.makeRequestURL) {
        return {}
      }
      this.data.makeRequestURL
        .split('?')[1]
        .split('&')
        .forEach((pair) => {
          pair = pair.split('=')
          params[pair[0]] = decodeURIComponent(pair[1])
        })
      return params
    },
    subject() {
      return this.params.subject || ''
    },
    body() {
      return this.params.body || ''
    },
    hideParams() {
      const a = []
      for (const k in this.params) {
        if (k.match(/hide_\w+/)) {
          a.push(k)
        }
      }
      return a
    },
    defaultLaw() {
      return selectBestLaw(this.publicBody.laws, LAW_TYPE)
    },
    authorityDescriptionHtml() {
      return this.data.authority_description.replace(
        /\[(.+)\]\(([^)]+)\)/g,
        '<a href="$2">$1</a>'
      )
    }
  },
  methods: {
    close() {
      this.$emit('close')
    },
    formSubmit() {
      this.submitting = true
      window.setTimeout(() => {
        this.$emit('requestmade', this.data)
        this.$emit('close')
      }, 300)
    }
  }
}
</script>

<style lang="scss" scoped>
.loading {
  height: 100vh;
  padding-top: 30%;
  background-color: var(--bs-body-bg);
  // animation: blinker 0.8s linear infinite;
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

.fake-markdown {
  white-space: pre-line;
}
</style>
