/* Shared page scripts (moved from index.html inline blocks).
   1) WHATSAPP_NUMBER me apna number daalo (country code ke saath, + ke bina, jaise "919876543210").
      Jab tak number sahi format me nahi hota, saare WhatsApp buttons apne aap chhupe rehte hain.
   2) Form me utm_* hidden fields judte hain, jo lead ke saath chale jaate hain.
   3) Google Analytics me "generate_lead" aur "whatsapp_click" events jaate hain.
   4) [data-plan] wale buttons click karne par form ka "interest" field us plan se bhar jaata hai. */
  (function () {
    var WHATSAPP_NUMBER = "918604275934";
    var message = encodeURIComponent("Hi, I'd like a demo of Vetra CRM.");
    var valid = /^\d{10,15}$/.test(WHATSAPP_NUMBER);

    document.querySelectorAll("[data-wa]").forEach(function (a) {
      if (!valid) { a.hidden = true; return; }
      a.href = "https://wa.me/" + WHATSAPP_NUMBER + "?text=" + message;
      a.target = "_blank";
      a.rel = "noopener noreferrer";
      a.hidden = false;
      a.addEventListener("click", function () {
        if (window.gtag) { gtag("event", "whatsapp_click", { location: a.getAttribute("data-wa") }); }
      });
    });

    var form = document.getElementById("contact-form");
    if (form) {
      var params = new URLSearchParams(window.location.search);
      ["utm_source", "utm_medium", "utm_campaign", "utm_content", "utm_term"].forEach(function (key) {
        var input = document.createElement("input");
        input.type = "hidden";
        input.name = key;
        input.value = params.get(key) || "";
        form.appendChild(input);
      });
      form.addEventListener("submit", function () {
        if (window.gtag) { gtag("event", "generate_lead", { form: "demo_request" }); }
      });
    }
  })();
  (function () {
    var header = document.querySelector(".header");
    if (header) {
      var onScroll = function () { header.classList.toggle("is-scrolled", window.scrollY > 8); };
      onScroll();
      window.addEventListener("scroll", onScroll, { passive: true });
    }

    var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (!("IntersectionObserver" in window) || reduce) { return; }

    var targets = document.querySelectorAll(".module-card, .plan-card, .product-screen, .how-grid article, .audience-list > div, .ai-spotlight, .compare-wrap, .faq-list details, .growth-band, .testi-card, .product-walkthrough, .video-takeaways article, .tier-card, .choice-card, .feature-items li, .steps-list li, .highlight-card, .journey-step, .seo-card, .seo-checklist");
    document.documentElement.classList.add("js-reveal");

    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          var el = entry.target;
          el.classList.add("is-visible");
          io.unobserve(el);
          setTimeout(function () {
            el.classList.remove("reveal-on", "is-visible");
            el.style.transitionDelay = "";
          }, 1000);
        }
      });
    }, { threshold: 0.12, rootMargin: "0px 0px -40px 0px" });

    targets.forEach(function (el, i) {
      el.classList.add("reveal-on");
      el.style.transitionDelay = ((i % 3) * 80) + "ms";
      io.observe(el);
    });
  })();

  (function () {
    document.querySelectorAll("[data-plan]").forEach(function (a) {
      a.addEventListener("click", function () {
        var select = document.querySelector("#contact-form [name='interest']");
        var value = a.getAttribute("data-plan");
        if (!select) { return; }
        for (var i = 0; i < select.options.length; i++) {
          if (select.options[i].text === value) { select.selectedIndex = i; break; }
        }
        if (window.gtag) { gtag("event", "plan_click", { plan: value }); }
      });
    });
  })();

  // Christmas offer: 26 Dec 2026 (IST) se offer bar/chip apne aap chhup jaate hain.
  (function () {
    if (Date.now() < Date.parse("2026-12-26T00:00:00+05:30")) { return; }
    document.querySelectorAll(".offer-bar, .offer-chip, .price-offer, .blog-lead-banner").forEach(function (el) { el.hidden = true; el.style.display = "none"; });
  })();
