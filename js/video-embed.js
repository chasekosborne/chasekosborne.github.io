/**
 * Click-to-play YouTube embeds.
 *
 * Markup:
 *   <div class="video-embed" data-youtube-id="VIDEO_ID" data-title="Title">
 *     <a class="video-poster" href="https://www.youtube.com/watch?v=VIDEO_ID" target="_blank">
 *       <img src="https://i.ytimg.com/vi/VIDEO_ID/hqdefault.jpg" alt="">
 *       <span class="video-play" aria-hidden="true"></span>
 *     </a>
 *   </div>
 *
 * YouTube rejects embeds that arrive without a Referer header (error 153),
 * which is what happens on file:// pages, so the player is only swapped in
 * when the page is served over http(s); otherwise the poster link opens
 * the video on YouTube.
 */
(function () {
    'use strict';

    if (!/^https?:$/.test(window.location.protocol)) return;

    document.querySelectorAll('.video-embed[data-youtube-id]').forEach(function (embed) {
        var poster = embed.querySelector('.video-poster');
        if (!poster) return;

        poster.addEventListener('click', function (e) {
            e.preventDefault();
            var iframe = document.createElement('iframe');
            iframe.src = 'https://www.youtube.com/embed/' + encodeURIComponent(embed.dataset.youtubeId) +
                '?autoplay=1&rel=0';
            iframe.title = embed.dataset.title || 'YouTube video player';
            iframe.allow = 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share';
            iframe.referrerPolicy = 'strict-origin-when-cross-origin';
            iframe.allowFullscreen = true;
            embed.replaceChild(iframe, poster);
        });
    });
})();
