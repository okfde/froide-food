{% load static %}
var CACHE_NAME = 'froide-food';

var PRECACHE_FILES = [
  '{% static "js/main.js" %}',
  '{% static "js/common.js" %}',
  '{% static "js/food.js" %}',
  '{% static "css/food.css" %}',
  '{% static "css/main.css" %}',
  '{% static "fonts/fontawesome-webfont.woff2" %}',
  '{% static "img/okfde.svg" %}',
  '{% static "food/manifest.json" %}',
];

STATIC_FILES = PRECACHE_FILES.slice();
STATIC_FILES = STATIC_FILES.concat([
  '{% static "food/images/yelp_stars.png" %}',
  '{% static "food/images/yelp_stars@2x.png" %}',
  '{% static "food/images/yelp_logo.png" %}',
  '{% static "food/icons/favicon.ico" %}',

  '{% static "food/icons/apple-touch-icon.png" %}',
  '{% static "food/icons/favicon-32x32.png" %}',
  '{% static "food/icons/favicon-16x16.png" %}',

  'https://media.frag-den-staat.de/files/media/thumbnails/23/15/2315a0d3-e795-4d62-a39f-1c6ad4577ee8/topf_secret.jpg__1140x0_q85_subject_location-1250%2C500_subsampling-2.jpg',
  'https://media.frag-den-staat.de/files/media/thumbnails/23/15/2315a0d3-e795-4d62-a39f-1c6ad4577ee8/topf_secret.jpg__940x0_q85_subject_location-1250%2C500_subsampling-2.jpg',
  'https://media.frag-den-staat.de/files/media/thumbnails/23/15/2315a0d3-e795-4d62-a39f-1c6ad4577ee8/topf_secret.jpg__768x0_q85_subject_location-1250%2C500_subsampling-2.jpg',

  'https://media.frag-den-staat.de/files/media/thumbnails/fa/3c/fa3c17ee-65ac-4473-af5b-3bf544b4fbc8/foodwatch-logo_ohne_claim_rgb_21cm_300dpi.jpg__1140x0_q85_subject_location-133%2C47_subsampling-2.jpg',
  'https://media.frag-den-staat.de/files/media/thumbnails/fa/3c/fa3c17ee-65ac-4473-af5b-3bf544b4fbc8/foodwatch-logo_ohne_claim_rgb_21cm_300dpi.jpg__940x0_q85_subject_location-133%2C47_subsampling-2.jpg',
  'https://media.frag-den-staat.de/files/media/thumbnails/fa/3c/fa3c17ee-65ac-4473-af5b-3bf544b4fbc8/foodwatch-logo_ohne_claim_rgb_21cm_300dpi.jpg__768x0_q85_subject_location-133%2C47_subsampling-2.jpg',

  'https://media.frag-den-staat.de/files/media/thumbnails/38/60/38604ee7-4d0c-4f4a-8347-ec30a0e03e39/frag_den_staat_logo_wide.png__1140x0_q85_subsampling-2.png',
  'https://media.frag-den-staat.de/files/media/thumbnails/38/60/38604ee7-4d0c-4f4a-8347-ec30a0e03e39/frag_den_staat_logo_wide.png__940x0_q85_subsampling-2.png',
  'https://media.frag-den-staat.de/files/media/thumbnails/38/60/38604ee7-4d0c-4f4a-8347-ec30a0e03e39/frag_den_staat_logo_wide.png__768x0_q85_subsampling-2.png',

]);

var MAIN_DOMAIN = '{{ SITE_URL }}';
var STATIC_URL = '{{ STATIC_URL }}';
var MEDIA_URL = '{{ STATIC_URL }}';
var STATIC_HTTP = STATIC_FILES[0].indexOf('http') === 0;

var matchUrl = /^(.*)(\.[a-f0-9]{12})\.(jpg|png|js|json|svg|gif|css)$/;

function normalize (url) {
  return url.replace(matchUrl, '$1.$3');
}

var CACHE_DICT = {}
for (var i = 0; i < STATIC_FILES.length; i += 1) {
  CACHE_DICT[STATIC_FILES[i]] = true;
}
var NORMALIZED_CACHE_DICT = {}
for (var i = 0; i < STATIC_FILES.length; i += 1) {
  NORMALIZED_CACHE_DICT[normalize(STATIC_FILES[i])] = true;
}

self.addEventListener('install', function(event) {
  event.waitUntil(
    caches.open(CACHE_NAME).then(function (cache) {
      cache.addAll(PRECACHE_FILES);
    })
  );
});

const fetchOptions = {
  mode: 'cors',
  credentials: 'omit',
  referrer: 'no-referrer'
}

self.addEventListener('fetch', function(event) {
  if (event.request.method !== 'GET') {
    return
  }
  if (event.request.url.indexOf(STATIC_URL) === -1 && event.request.url.indexOf(MEDIA_URL) === -1) {
    return
  }
  event.respondWith(
    caches.open(CACHE_NAME).then(function(cache) {
      return cache.match(event.request).then(function (response) {
        return response || fetch(event.request, fetchOptions).then(function(response) {
          cache.put(event.request, response.clone());
          return response;
        });
      });
    })
  );
});

self.addEventListener('activate', function(event) {
  event.waitUntil(
    caches.open(CACHE_NAME).then(function (cache) {
      cache.keys().then(function(keys) {
        keys.forEach(function(request, index, array) {
          var key = request.url;
          if (!STATIC_HTTP) {
            key = key.replace(MAIN_DOMAIN, '');
          }
          if (CACHE_DICT[key] === undefined) {
            var normalizedKey = normalize(key)
            if (NORMALIZED_CACHE_DICT[normalizedKey] !== undefined) { 
              cache.delete(request);
            }
          }
        });
      });
    })
  );
});
