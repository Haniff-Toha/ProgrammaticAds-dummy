import streamlit as st
import pandas as pd
import os
import numpy as np
import io
import altair as alt
import random
from datetime import datetime, timedelta

# ---- Dummy data ----
def generate_dummy_creatives(n=10):
    categories = ['alcohol', 'smoking', 'violence', 'gambling', 'safe', 'political', 'adult']
    sensitivity_map = { 'safe': 'Mild', 'political': 'Normal', 'gambling': 'High',
                        'alcohol': 'High', 'smoking': 'Mild', 'violence': 'High', 'adult': 'High'}

    data = []
    for i in range(n):
        category = random.choices(categories, weights=[2, 2, 1, 1, 5, 1, 1])[0]
        status = 'approved' if category == 'safe' else 'pending review'
        content_type = random.choice(['image', 'text', 'video'])
        sensitivity = sensitivity_map[category]
        
        data.append({
            'creative_id': f'C{i:03}',
            'content_type': content_type,
            'filename': f'ad_{i:03}.{ "jpg" if content_type=="image" else "txt" if content_type=="text" else "mp4"}',
            'client': random.choice(['Coca-Cola', 'Marlboro', 'Nike', 'Heineken', 'GreenPeace']),
            'upload_date': datetime.today().date() - timedelta(days=random.randint(0, 5)),
            'predicted_category': category,
            'content_sensitivity': sensitivity,
            'status': status
        })
    return pd.DataFrame(data)

# df = generate_dummy_creatives()

def generate_dummy_slots(n=15):
    statuses = ['booked', 'available', 'predicted_empty']
    screens = ['SC-JKT-01', 'SC-BDG-01', 'SC-SBY-01']
    locations = ['long/lat-Stasiun A', 'long/lat-Jalan B', 'long/lat jalan C']

    data = []
    now = datetime.now()

    for i in range(n):
        screen = random.choice(screens)
        location = random.choice(locations)
        start = now + timedelta(minutes=30 * i)
        end = start + timedelta(minutes=30)
        status = random.choices(statuses, weights=[5, 3, 2])[0]
        price = random.randint(250_000, 750_000)  # in Rupiah
        data.append({
            'screen_board_id': screen,
            'location': location,
            'price': price,
            'start_time': start.strftime('%Y-%m-%d %H:%M'),
            'end_time': end.strftime('%Y-%m-%d %H:%M'),
            'status': status,
            'booked_by': random.choice(['Coca-Cola', 'Nike', 'Unilever', '']) if status == 'booked' else '',
            'fallback_flag': 'Yes' if status == 'predicted_empty' else 'No'
        })
    return pd.DataFrame(data)

#==============================================================================================================

# ---- Streamlit UI ----
import streamlit as st
 
st.title('Programmatic Ads Dashboard')

with st.sidebar:
    
    st.text('[Logo Client]')

    st.text('About Us')
    st.text('Our Products')
    # st.text('')
    # genre = st.selectbox(
    #     label="Pilih Lokasi",
    #     options=('Jakarta', 'Bandung', 'Surabaya')
    # )
    
    # values = st.slider(
    #     label='Select a range of values',
    #     min_value=0, max_value=100, value=(0, 100)
    # )
    # st.write('Values:', values)


AdApproval, SpaceManagement, AdsSceduller, DashInsight, GeoView = st.tabs(["AI-Based Ad Approval", "Slot Management", "Playback Schedule", "Performance Insights", "Geospatial View"])

with AdApproval:
    st.title("🎯 AI-Based Ad Approval")

    col_upload, col_sim = st.columns([2, 1])
    with col_upload:
        content_type = st.radio("Pilih Tipe Konten", ["image", "video", "text"], horizontal=True)

        # Initialize session state
        if "df_creatives" not in st.session_state:
            st.session_state.df_creatives = pd.DataFrame()

        uploaded_file = None
        typed_text = ""

        if content_type in ["image", "video"]:
            uploaded_file = st.file_uploader(f"📁 Upload file konten ({content_type.upper()})", type=["jpg", "jpeg", "png", "mp4"])
        elif content_type == "text":
            typed_text = st.text_area("📝 Masukkan Konten Teks")

        st.info("Silakan unggah file atau masukkan teks, atau gunakan data simulasi.")
    with col_sim:
        if st.button("🚀 Gunakan Data Simulasi"):
            st.session_state.df_creatives = generate_dummy_creatives()

    # Process uploaded file
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        st.session_state.df_creatives = df

    # If data exists, show DataFrame and review logic
    if not st.session_state.df_creatives.empty:
        df = st.session_state.df_creatives

        col_header, col_refresh = st.columns([3, 1])
        with col_header:
            st.subheader("📋 Data Kreatif Terkini")
        with col_refresh:
            if st.button("🔄 Refresh Data"):
                st.rerun()
        st.dataframe(df, use_container_width=True)

        pending_df = df[df["status"] == "pending review"]

        if pending_df.empty:
            st.success("Tidak ada kreatif yang perlu ditinjau.")
        else:
            st.subheader("🚦 Review Konten")
            pending_df = df[df["status"] == "pending review"]

            if pending_df.empty:
                st.success("Tidak ada kreatif yang perlu ditinjau.")
            else:
                selected_id = st.selectbox(
                    "Pilih Creative ID untuk direview:",
                    options=pending_df["creative_id"].tolist()
                )

                selected_row = pending_df[pending_df["creative_id"] == selected_id].iloc[0]

                st.markdown(f"### 📄 Detail Kreatif: `{selected_row['creative_id']}`")
                st.text(f"Client: {selected_row['client']}")
                st.text(f"Upload Date: {selected_row['upload_date']}")
                st.text(f"Predicted Category: {selected_row['predicted_category']}")
                st.text(f"Content Type: {selected_row['content_type']}")
                st.text(f"File: {selected_row['filename']}")

                # Content Preview
                st.markdown("#### 🖼️ Pratinjau Konten:")
                if selected_row["content_type"] == "image":
                    st.image("https://via.placeholder.com/300x180.png?text=Image+Preview")
                elif selected_row["content_type"] == "video":
                    st.video("https://www.w3schools.com/html/mov_bbb.mp4")
                elif selected_row["content_type"] == "text":
                    st.text("Ini adalah isi simulasi konten teks.")

                # Approve / Reject Buttons
                colA, colB = st.columns(2)
                with colA:
                    if st.button("✅ Approve"):
                        df.loc[df["creative_id"] == selected_id, "status"] = "approved"
                        st.success(f"{selected_id} telah disetujui.")
                with colB:
                    if st.button("❌ Reject"):
                        df.loc[df["creative_id"] == selected_id, "status"] = "rejected"
                        st.error(f"{selected_id} telah ditolak.")


        # st.markdown("---")
        # st.subheader("📦 Status Review Terkini")
        # st.dataframe(df, use_container_width=True)
#===============================================================================================================================
 
with SpaceManagement:
    st.header("Slot/Space Management")
    # ---- 2. Load once in session ----
    if "slot_df" not in st.session_state:
        st.session_state.slot_df = generate_dummy_slots()

    slot_df = st.session_state.slot_df

    # ---- 4. Filters ----
    with st.expander("🔍 Filter Slot yang Tersedia"):
        selected_location = st.selectbox("Pilih Lokasi", ["Semua"] + sorted(slot_df["location"].unique()))
        selected_status = st.multiselect("Status Slot", ["booked", "available", "predicted_empty"], default=["available", "predicted_empty"])
        price_range = st.slider("Harga Slot (Rupiah)", 0, 1000000, (200000, 800000), step=50000)

    # ---- 5. Filter logic ----
    filtered_df = slot_df.copy()

    if selected_location != "Semua":
        filtered_df = filtered_df[filtered_df["location"] == selected_location]

    if selected_status:
        filtered_df = filtered_df[filtered_df["status"].isin(selected_status)]

    filtered_df = filtered_df[
        (filtered_df["price"] >= price_range[0]) & (filtered_df["price"] <= price_range[1])
    ]

    # ---- 6. Show filtered table ----
    st.subheader("📊 Jadwal Slot Iklan")
    st.dataframe(filtered_df.sort_values("start_time"), use_container_width=True)
    
    csv_buffer = io.StringIO()
    filtered_df.to_csv(csv_buffer, index=False)
    csv_data = csv_buffer.getvalue()
    
    st.download_button(
        label="📤 Export to CSV",
        data=csv_data,
        file_name="filtered_slot_data.csv",
        mime="text/csv"
    )
    with st.expander("✏️ Edit Slot"):
        editable_ids = filtered_df["screen_board_id"].tolist()
        
        if not editable_ids:
            st.info("Tidak ada slot yang dapat diedit dari hasil filter.")
        else:
            selected_screen_board_id = st.selectbox("Pilih Slot ID untuk diedit", editable_ids)

            # Get the selected row from the full dataframe
            editable_row = slot_df[slot_df["screen_board_id"] == selected_screen_board_id].iloc[0]

            # Ensure datetime conversion
            start_dt = pd.to_datetime(editable_row["start_time"])
            end_dt = pd.to_datetime(editable_row["end_time"])


            # Editable form
            new_status = st.selectbox("Status", ["booked", "available", "predicted_empty"], index=["booked", "available", "predicted_empty"].index(editable_row["status"]))
            new_price = st.number_input("Harga Slot", min_value=0, max_value=1000000, value=int(editable_row["price"]), step=50000)
            new_start = st.time_input("Waktu Mulai", start_dt.time()) 
            new_end = st.time_input("Waktu Selesai", end_dt.time())   


            if st.button("💾 Simpan Perubahan"):
                # Apply changes directly to session state
                idx = slot_df[slot_df["screen_board_id"] == selected_screen_board_id].index[0]
                st.session_state.slot_df.at[idx, "status"] = new_status
                st.session_state.slot_df.at[idx, "price"] = new_price
                st.session_state.slot_df.at[idx, "start_time"] = datetime.combine(editable_row["start_time"].date(), new_start)
                st.session_state.slot_df.at[idx, "end_time"] = datetime.combine(editable_row["end_time"].date(), new_end)

                st.success(f"Slot `{selected_screen_board_id}` berhasil diperbarui.")
                st.rerun()


    # ---- 7. Manual Booking Section (DSP- untuk client) ----
    # st.subheader("📝 Reservasi Slot Manual")

    # available_slots = filtered_df[
    #     filtered_df["status"].isin(["available", "predicted_empty"])
    # ]

    # if available_slots.empty:
    #     st.info("Tidak ada slot yang tersedia untuk dipesan.")
    # else:
    #     selected_slot = st.selectbox("Pilih Slot:", available_slots["screen_board_id"])
    #     selected_slot_info = available_slots[available_slots["screen_board_id"] == selected_slot].iloc[0]

    #     st.markdown(f"""
    #     **Screen:** {selected_slot_info['screen_board_id']}  
    #     **Lokasi:** {selected_slot_info['location']}  
    #     **Waktu:** {selected_slot_info['start_time']} - {selected_slot_info['end_time']}  
    #     **Harga:** Rp {selected_slot_info['price']:,}
    #     """)

    #     advertiser_name = st.text_input("Nama Advertiser")
    #     if st.button("✅ Konfirmasi Reservasi"):
    #         idx = slot_df[slot_df["screen_board_id"] == selected_slot].index[0]
    #         slot_df.at[idx, "status"] = "booked"
    #         slot_df.at[idx, "booked_by"] = advertiser_name
    #         slot_df.at[idx, "fallback_flag"] = "No"
    #         st.success(f"Slot {selected_slot} berhasil dipesan untuk {advertiser_name}.")
#=================================================================================================
 
with AdsSceduller:
    st.header("Playback Schedule")
    st.subheader('[Akan ditambahkan based on AI Recommendation]')
    # ---- 1. Dummy data: filter approved creatives ----
    if "df_creatives" in st.session_state:
        creatives_df = st.session_state.df_creatives
        approved_creatives = creatives_df[creatives_df["status"] == "approved"]
    else:
        st.warning("Belum ada data kreatif disetujui. Gunakan tab Ad Approval terlebih dahulu.")
        approved_creatives = pd.DataFrame()

    # ---- 2. Dummy data: filter booked slots ----
    if "slot_df" in st.session_state:
        slots_df = st.session_state.slot_df
        booked_slots = slots_df[slots_df["status"] == "booked"]
    else:
        st.warning("Belum ada slot dipesan. Gunakan tab Slot Management terlebih dahulu.")
        booked_slots = pd.DataFrame()

    # ---- 3. Simulate Schedule by randomly assigning creatives to slots ----
    if not approved_creatives.empty and not booked_slots.empty:
        creative_pool = approved_creatives.reset_index(drop=True)
        schedule = []

        for i, row in booked_slots.iterrows():
            if len(creative_pool) == 0:
                break
            chosen = creative_pool.sample(1).iloc[0]
            schedule.append({
                'screen_board_id': row['screen_board_id'],
                'location': row['location'],
                'start_time': row['start_time'],
                'end_time': row['end_time'],
                'client': row['booked_by'],
                'creative_id': chosen['creative_id'],
                'content_type': chosen['content_type'],
                'filename': chosen['filename']
            })
            creative_pool = creative_pool.drop(creative_pool[creative_pool["creative_id"] == chosen["creative_id"]].index)

        schedule_df = pd.DataFrame(schedule)
        st.subheader("📋 Jadwal Penayangan Otomatis")
        st.dataframe(schedule_df.sort_values("start_time"), use_container_width=True)
    else:
        st.info("Belum tersedia data kreatif atau slot untuk menjadwalkan iklan.")

    # ---- 4. Manual Assignment Tool ----
    st.markdown("---")
    st.subheader("✍️ Penjadwalan Manual Iklan")

    available_slots = booked_slots.copy()
    available_creatives = approved_creatives.copy()

    if not available_slots.empty and not available_creatives.empty:
        selected_slot = st.selectbox("Pilih Slot:", available_slots["screen_board_id"])
        selected_creative = st.selectbox("Pilih Kreatif:", available_creatives["creative_id"])

        selected_slot_info = available_slots[available_slots["screen_board_id"] == selected_slot].iloc[0]
        selected_creative_info = available_creatives[available_creatives["creative_id"] == selected_creative].iloc[0]

        st.markdown(f"""
        **Slot/Screen:** `{selected_slot_info['screen_board_id']}`  
        **Lokasi:** `{selected_slot_info['location']}`  
        **Waktu:** {selected_slot_info['start_time']} – {selected_slot_info['end_time']}  
        **Kreatif/Konten:** `{selected_creative_info['filename']}`  
        **Kategori:** `{selected_creative_info['predicted_category']}`
        ### **Harga:** Rp {selected_slot_info['price']:,}
        """)

        if st.button("🗓️ Jadwalkan Iklan"):
            st.success(f"Iklan {selected_creative} telah dijadwalkan ke slot {selected_slot}.")

    else:
        st.info("Belum ada kreatif disetujui atau slot tersedia.")

#=========================================================================================================

with DashInsight:
    st.header("📊 Performance Insights Dashboard")

    # ---- Use dummy slot data ----
    if "slot_df" not in st.session_state:
        st.warning("Data slot belum dimuat.")
        st.stop()

    slot_df = st.session_state.slot_df

    # ---- 1. Simulate Impressions ----
    # We'll simulate impressions based on screen & time
    slot_df["estimated_impressions"] = slot_df["status"].apply(lambda s: random.randint(500, 2000) if s == "booked" else random.randint(50, 300))
    slot_df["revenue"] = slot_df.apply(lambda row: row["price"] if row["status"] == "booked" else 0, axis=1)

    # ---- 2. KPI Cards ----
    total_slots = len(slot_df)
    booked_slots = len(slot_df[slot_df["status"] == "booked"])
    fill_rate = (booked_slots / total_slots) * 100 if total_slots > 0 else 0
    total_impressions = slot_df["estimated_impressions"].sum()
    total_revenue = slot_df["revenue"].sum()

    col1, col2, col3 = st.columns(3)
    col1.metric("🎯 Slot Fill Rate", f"{fill_rate:.1f}%", delta=f"{booked_slots} / {total_slots}")
    col2.metric("👁️ Total Estimated Impressions", f"{total_impressions:,}")
    col3.metric("💰 Estimated Revenue (Rp)", f"{total_revenue:,.0f}")

    # ---- 3. Bar Chart by Location ----
    location_summary = slot_df.groupby("location").agg({
        "estimated_impressions": "sum",
        "revenue": "sum",
        "screen_board_id": "count"
    }).reset_index().rename(columns={"screen_board_id": "total_slots"})

    st.subheader("📍 Impressions & Revenue by Location")

    chart = alt.Chart(location_summary).mark_bar().encode(
        x=alt.X("location:N", title="Lokasi"),
        y=alt.Y("estimated_impressions:Q", title="Impressions"),
        color=alt.Color("revenue:Q", scale=alt.Scale(scheme="blues"), title="Pendapatan"),
        tooltip=["location", "estimated_impressions", "revenue"]
    ).properties(width=600)

    st.altair_chart(chart, use_container_width=True)

    # ---- 4. Table View ----
    st.subheader("📋 Tabel Ringkasan Slot")
    st.dataframe(slot_df[[
        "screen_board_id", "location", "start_time", 
        "status", "estimated_impressions", "price", "revenue"
    ]], use_container_width=True)


with GeoView:
    st.header("Geospatial View")
    # still use dummy data, add geolocation for simulation
    if "latitude" not in st.session_state.slot_df.columns:
        np.random.seed(42)
        st.session_state.slot_df["latitude"] = st.session_state.slot_df["location"].apply(lambda x: {
            "Stasiun A": -6.2,
            "Stasiun B": -6.3,
            "Stasiun C": -6.25
        }.get(x, -6.2) + np.random.uniform(-0.01, 0.01))

        st.session_state.slot_df["longitude"] = st.session_state.slot_df["location"].apply(lambda x: {
            "Stasiun A": 106.8,
            "Stasiun B": 106.85,
            "Stasiun C": 106.75
        }.get(x, 106.8) + np.random.uniform(-0.01, 0.01))
    
    st.header("🗺️ Geospatial View of Screens")

    # Use filtered slot data
    slot_df = st.session_state.slot_df

    # Filter booked + available for map
    map_data = slot_df[slot_df["status"].isin(["booked", "available", "predicted_empty"])][[
       "screen_board_id", "location", "status", "latitude", "longitude", "estimated_impressions"
    ]]

    st.map(map_data.rename(columns={"latitude": "lat", "longitude": "lon"}))

    st.markdown("---")
    st.subheader("📋 Ringkasan Lokasi & Status Slot")
    st.dataframe(map_data, use_container_width=True)

