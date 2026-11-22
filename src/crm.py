"""
Vetra CRM ke saare features — ek hi jagah.
Isse /features/ page ke sections aur /cloud-crm/ ka comparison table dono bante hain.
plans: "S" = Starter, "G" = Growth, "P" = Pro  (Self-Hosted me sab kuch hota hai)
"""
from html import escape as esc

ALL, GP, P = "SGP", "GP", "P"

GROUPS = [
    ("lead-capture", "Lead capture", "↗", "Lead capture from IndiaMART, Google Ads, Facebook Ads and your website", "All plans",
     "Every enquiry lands in one CRM, no matter where it comes from. Your team gets a notification and the customer gets an instant email reply that matches what they asked for.",
     [("IndiaMART lead integration", "Buyer enquiries from your connected IndiaMART account come into the CRM automatically, with the product and requirement attached.", ALL),
      ("Google Ads and Facebook / Meta lead forms", "Leads from connected Google Ads and Meta (Facebook and Instagram) lead forms are added to your pipeline without copy-paste.", ALL),
      ("Custom pages and website forms", "Connect any landing page, website form or custom source to the CRM through the lead API or webhook.", ALL),
      ("Instant new-lead notifications", "The right people are alerted the moment a new lead arrives, so no enquiry waits.", ALL),
      ("Automatic email reply", "Each new lead gets an automatic email reply based on their requirement, even outside office hours.", ALL),
      ("Complete lead history and timeline", "Every status change, note, message, quotation and payment is saved in the lead's timeline.", ALL)]),
    ("lead-assignment", "Assignment & pipeline", "⇄", "Automatic lead assignment and sales pipeline", "All plans",
     "Decide who gets which lead, and who can see what. Your team tracks and updates every lead status from enquiry to order.",
     [("Sales pipeline with lead status", "Users track and update lead status at every stage, from new enquiry to order placed.", ALL),
      ("Manual assign and reassign", "Admins and managers can assign or move leads between team members at any time.", ALL),
      ("Round-robin auto-assignment", "New leads are shared evenly across your sales team automatically.", GP),
      ("Assign by user or role", "Route leads to a specific user or to everyone in a role, such as a regional sales team.", GP),
      ("Lead visibility rules", "Choose whether users see all leads or only the leads assigned to them.", GP)]),
    ("follow-ups", "Notes & follow-ups", "◷", "Smart notes, follow-ups and reminders", "All plans",
     "Follow-ups that remind you before they are due, so no customer is forgotten.",
     [("Smart notes", "Keep customer context, call notes and requirements next to the lead.", ALL),
      ("Follow-ups and reminders", "Set a follow-up or reminder and get notified before it is due.", ALL),
      ("Tasks for calls and meetings", "Plan calls, meetings and other work so every next step has an owner and a time.", ALL)]),
    ("quotations-payments", "Quotations & payments", "▤", "Quotations with payment links, and automatic orders", "All plans",
     "Send a quotation with a payment link. When the customer pays, the CRM is notified, the order is placed and the lead is updated automatically.",
     [("Multi-product quotations", "Build quotations with multiple products, quantities and prices in a few clicks.", ALL),
      ("Payment link in every quotation", "Customers can pay directly from the quotation you send.", ALL),
      ("Automatic order on payment", "When a payment is received, the CRM is notified, the order is placed and the lead is marked as converted.", ALL),
      ("Quotation viewed alerts", "Know when a customer opens the quotation so you can follow up at the right time.", ALL),
      ("Multiple payment gateways", "Configure more than one payment gateway and choose which one to use.", GP),
      ("Coupons and offers", "Create coupons and offers and share them with customers on email or WhatsApp.", GP)]),
    ("whatsapp-crm", "WhatsApp CRM", "✉", "WhatsApp CRM: chat with customers from the CRM", "Growth & Pro",
     "Connect the WhatsApp Business API and chat with customers directly from Vetra. Share products, quotations, orders, coupons and ticket updates inside the chat.",
     [("WhatsApp Business API connection", "Connect your WhatsApp Business API number to the CRM.", GP),
      ("Two-way WhatsApp chat", "Your team chats with customers on WhatsApp right inside the CRM, with the full history saved.", GP),
      ("Share products, quotations and coupons", "Send product details, quotations and coupon codes in the chat in one click.", GP),
      ("Order and support ticket status", "Send order details, order status and support ticket status to the customer on WhatsApp.", GP)]),
    ("ai-agent", "AI agent", "✦", "AI sales and support agent for WhatsApp", "Pro & Self-Hosted",
     "Connect your AI provider's API key and the AI agent talks to customers like a sales and support executive, with no human needed for routine questions.",
     [("Product enquiries", "Answers product questions and helps customers with their requirements, like a sales person would.", P),
      ("Order status and order queries", "Looks up the customer's order and shares its status automatically.", P),
      ("Support issues and tickets", "Handles support questions and creates a support ticket in the CRM when needed.", P),
      ("Hand-off to a human", "For critical or sensitive conversations, the AI transfers the chat to a human agent automatically.", P)]),
    ("marketing", "Email & WhatsApp marketing", "◉", "Email marketing, WhatsApp marketing and templates", "All plans",
     "Plan campaigns, schedule email and WhatsApp messages, and see which emails were opened.",
     [("Built-in email templates", "Start with ready-made templates for replies, quotations and follow-ups.", ALL),
      ("Custom email templates", "Create your own templates for any message your team sends often.", ALL),
      ("Multiple sender email accounts", "Attach different email accounts to different templates and teams.", GP),
      ("Email open tracking", "See whether each email you sent was opened or not.", GP),
      ("Scheduled email campaigns", "Plan email marketing campaigns and send them at the time you choose.", GP),
      ("Scheduled WhatsApp campaigns", "Schedule WhatsApp marketing messages with approved templates and coupons.", GP)]),
    ("orders-delivery", "Orders & delivery", "⛟", "Order management, delivery tracking, returns and refunds", "All plans",
     "Track every order from placement to delivery, and handle returns, refunds and support from the CRM without opening your payment gateway portal.",
     [("Order management", "See every order, its items, payment status and customer in one register.", ALL),
      ("Delivery tracking with multiple providers", "Connect tracking providers such as 17TRACK and USPS and follow shipments from the CRM.", GP),
      ("Returns and refunds management", "Handle return and refund requests from the CRM, without going to the payment gateway portal.", GP),
      ("Support tickets", "Log, assign and resolve customer issues with a clear status for each ticket.", GP)]),
    ("inventory", "Products & inventory", "▦", "Products, inventory, purchases and GST invoices", "All plans",
     "Manage your catalogue, stock and purchases, and generate GST invoices from the same place you sell.",
     [("Product listing", "Maintain your product catalogue with prices, details and images.", ALL),
      ("Inventory management", "Track stock levels as orders are placed.", ALL),
      ("GST invoice generation", "Generate GST invoices for orders directly from the CRM.", ALL),
      ("Media management", "Images, invoices and documents are stored and organised in the CRM media library.", ALL),
      ("Purchase management", "Record purchases from suppliers and keep inventory up to date.", GP)]),
    ("dashboard-reports", "Dashboard & reports", "▥", "CRM dashboard and detailed reports", "All plans",
     "A dashboard that summarises leads, orders, payments, tickets and team activity, with detailed reports when you need to dig in.",
     [("Business dashboard", "See leads, pipeline, orders, payments and team activity in one summary.", ALL),
      ("Detailed CRM reports", "Full reports on leads, sales, orders, campaigns and team activity.", P)]),
    ("admin-security", "Admin, roles & security", "♙", "Admin controls, user roles, permissions and audit logs", "All plans",
     "Admins control every part of the CRM from settings: users, roles, permissions, lead rules, login security and logs.",
     [("Admin settings for every module", "Configure how each part of the CRM works for your business.", ALL),
      ("Users and team access", "Add users for your sales, support and operations teams.", ALL),
      ("Login security", "Choose password-only, password plus OTP, or OTP-only login.", ALL),
      ("Custom roles and permissions", "Create roles and control exactly what each role can see and do.", GP),
      ("Audit log", "Review important changes made in the CRM and who made them.", GP),
      ("Login, authorization and activity logs", "See every user's activity, logins and authorization events.", P),
      ("Error and general system logs", "Admins can review error logs and general logs for the workspace.", P)]),
    ("storefront-api", "Online store API", "⌘", "Online store API: build your e-commerce website on Vetra", "Pro & Self-Hosted",
     "Use the Vetra storefront API to build your own e-commerce website in Next.js or React. Products, stock and coupons come from the CRM, and every order lands back in the CRM.",
     [("Storefront API", "Build a custom online store in Next.js, React or any front-end framework.", P),
      ("Orders managed in the CRM", "Website orders appear in the CRM with payments, delivery tracking and support.", P),
      ("One catalogue for every channel", "Products, inventory and coupons stay in sync between the CRM and your store.", P)]),
]


def plan_label(p):
    return {ALL: "", GP: "Growth & Pro", P: "Pro & Self-Hosted"}[p]


def features_nav():
    return '<nav class="fnav" aria-label="Feature sections"><div class="wrap">' + "".join(
        f'<a href="#{g[0]}">{esc(g[1])}</a>' for g in GROUPS) + "</div></nav>"


def features_groups():
    out = []
    for gid, short, icon, title, plans, lede, items in GROUPS:
        lis = "".join(
            f'<li><b>{esc(n)}</b><p>{esc(t)}</p>' + (f'<span class="plan-tag">{plan_label(p)}</span>' if plan_label(p) else "") + "</li>"
            for n, t, p in items)
        tag_cls = "plan-tag orange" if plans != "All plans" else "plan-tag"
        out.append(f'''<section class="fgroup" id="{gid}" aria-labelledby="{gid}-title">
  <div class="fgroup-head"><span class="{tag_cls}">{esc(plans)}</span><h2 id="{gid}-title">{esc(title)}</h2><p>{esc(lede)}</p></div>
  <ul class="fitems">{lis}</ul>
</section>''')
    return '<div class="wrap">' + "\n".join(out) + "</div>"


def matrix():
    rows = []
    for gid, short, *_ , items in GROUPS:
        rows.append(f'<tr class="group"><th colspan="4" scope="colgroup">{esc(short)}</th></tr>')
        for n, _t, p in items:
            cells = "".join('<td class="y">✓ Included</td>' if k in p else '<td class="n">– Not included</td>' for k in "SGP")
            rows.append(f'<tr><th scope="row">{esc(n)}</th>{cells}</tr>')
    return ('<div class="table-wrap"><table class="ctable"><caption class="sr-only">Vetra Cloud CRM plan comparison</caption>'
            '<thead><tr><th scope="col">Feature</th><th scope="col">Starter</th><th scope="col">Growth</th><th scope="col">Pro</th></tr></thead><tbody>'
            + "".join(rows) + "</tbody></table></div>")


def feature_list_flat():
    return [n for g in GROUPS for n, _t, _p in g[6]]


PLANS = [
    ("starter", "Starter", "For small teams that want every lead captured and followed up.", "Up to 3 users", "₹1,999", "₹1,599", False,
     ["IndiaMART, Google Ads, Facebook Ads and website leads", "New-lead alerts and automatic email replies", "Sales pipeline with full lead timeline",
      "Smart notes, follow-ups and reminders", "Quotations with payment links", "Automatic order when the customer pays",
      "Products, inventory and GST invoices", "Dashboard, users and OTP login security"], "Includes"),
    ("growth", "Growth", "For growing sales teams selling on WhatsApp and running campaigns.", "Up to 10 users", "₹4,999", "₹3,999", True,
     ["Round-robin and role-based lead assignment", "Lead visibility rules", "WhatsApp API chat inside the CRM",
      "Send products, quotes, orders and coupons on WhatsApp", "Multiple payment gateways, coupons and offers", "Scheduled email and WhatsApp campaigns",
      "Email open tracking and multiple senders", "Delivery tracking (17TRACK, USPS and more)", "Support tickets, returns and refunds",
      "Purchase management, custom roles and audit log"], "Everything in Starter, plus"),
    ("pro", "Pro", "For businesses that want AI on WhatsApp, an online store and full control.", "Up to 25 users", "₹9,999", "₹7,999", False,
     ["AI sales and support agent on WhatsApp", "AI shares order status and creates tickets", "Automatic hand-off to a human",
      "Storefront API for your Next.js or React store", "Website orders managed in the CRM", "Detailed CRM reports",
      "Login, authorization, activity, error and general logs"], "Everything in Growth, plus"),
]


def plans_html(detailed=False):
    cards = []
    for pid, name, who, users, price, offer, pop, feats, lead in PLANS:
        fl = feats if detailed else feats[:4]
        lead_html = f'<p class="who" style="margin-top:18px;color:var(--ink);font-weight:700">{lead}</p>' if detailed else ""
        cards.append(f'''<article class="plan{' pop' if pop else ''} choice-card" id="plan-{pid}">
  {'<span class="badge">MOST POPULAR</span>' if pop else ''}
  <h3>Vetra {name}</h3><p class="who">{esc(who if detailed else users)}</p>
  <div class="price"><b>{price}</b><span>/month + GST</span></div>
  <p class="who">{users} · billed monthly</p>
  <p class="price-offer">✦ Christmas offer: {offer}/month till 25 Dec</p>
  {lead_html}<ul>{"".join(f"<li>{esc(f)}</li>" for f in fl)}</ul>
  <a class="btn {'btn-primary' if pop else 'btn-ghost'}" href="#contact" data-plan="Cloud CRM: {name} plan">Start with {name}</a>
</article>''')
    selfhost = '''<div class="selfhost" id="plan-self-hosted-teaser">
  <div><small>VETRA SELF-HOSTED</small><h3>The complete CRM on your own server</h3><p>Every Pro feature, installed on your server. Your data stays with you.</p></div>
  <ul><li>Your VPS or data centre</li><li>Installed &amp; trained by us</li><li>Support ₹29,999/year (optional)</li></ul>
  <div class="sh-price"><span>One-time license from</span><b>₹1,49,999</b><a class="btn btn-light" href="/self-hosted-crm/">Explore Self-Hosted</a></div>
</div>'''
    return '<div class="plans">' + "".join(cards) + "</div>" + selfhost
