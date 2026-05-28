/*Application Package Name: com.tiktok.lite.go
class PRCS_394 {
/**
X.3Rv;L(Landroid/accounts/AccountManager; Ljava/lang/String; [Ljava/lang/String; Ljava/lang/String;)Landroid/accounts/AccountManagerFuture;
*/

    public static android.accounts.AccountManagerFuture L(android.accounts.AccountManager p17, String p18, String[] p19, String p20)
    {
        com.bytedance.helios.statichook.api.HeliosApiHook v5_1 = new com.bytedance.helios.statichook.api.HeliosApiHook();
        Object[] v11 = new Object[4];
        v11[0] = p18;
        v11[1] = p19;
        v11[2] = 0;
        v11[3] = 0;
        com.bytedance.helios.statichook.api.ExtraInfo v12_1 = new com.bytedance.helios.statichook.api.ExtraInfo(0, "(Ljava/lang/String;[Ljava/lang/String;Landroid/accounts/AccountManagerCallback;Landroid/os/Handler;)Landroid/accounts/AccountManagerFuture;", p20);
        com.bytedance.helios.statichook.api.Result v1_0 = v5_1.preInvoke(102502, "android/accounts/AccountManager", "getAccountsByTypeAndFeatures", p17, v11, "android.accounts.AccountManagerFuture", v12_1);
        if (!v1_0.intercept) {
            android.accounts.AccountManagerFuture v6_1 = p17.getAccountsByTypeAndFeatures(p18, p19, 0, 0);
            v5_1.postInvoke(v6_1, 102502, "android/accounts/AccountManager", "getAccountsByTypeAndFeatures", p17, v11, v12_1, 1);
            return v6_1;
        } else {
            v5_1.postInvoke(0, 102502, "android/accounts/AccountManager", "getAccountsByTypeAndFeatures", p17, v11, v12_1, 0);
            return ((android.accounts.AccountManagerFuture) v1_0.returnValue);
        }
    }

/**
X.3Rv;LBL()Z
*/

    public final boolean LBL()
    {
        this.ac_();
        Boolean v1_4 = this.LIIII.LFF.L();
        if ((v1_4 - this.LB) > 86400000) {
            this.L = 0;
        }
        Boolean v3_11 = this.L;
        if (v3_11 != null) {
            return v3_11.booleanValue();
        } else {
            android.accounts.AccountManager v5_3;
            android.content.Context v7 = this.LIIII.L;
            com.bytedance.helios.statichook.api.HeliosApiHook v11_1 = new com.bytedance.helios.statichook.api.HeliosApiHook();
            X.3Oo v4_2 = new Object[2];
            v4_2[0] = v7;
            v4_2[1] = "android.permission.GET_ACCOUNTS";
            com.bytedance.helios.statichook.api.ExtraInfo v9_1 = new com.bytedance.helios.statichook.api.ExtraInfo(0, "(Landroid/content/Context;Ljava/lang/String;)I", "dzBzEgU1UM3QUBkgSxaWaaw9Bz14/yzxe1dYm0ZJPLqwOID9zPVdd3eEmUDB28GN");
            com.bytedance.helios.statichook.api.HeliosApiHook v11_2 = v11_1;
            android.accounts.AccountManager v5_2 = v11_2.preInvoke(2908, "androidx/core/content/ContextCompat", "checkSelfPermission", X.04U, v4_2, "int", v9_1);
            if (!v5_2.intercept) {
                v5_3 = X.04U.L(v7, "android.permission.GET_ACCOUNTS");
                v11_2.postInvoke(Integer.valueOf(v5_3), 2908, "androidx/core/content/ContextCompat", "checkSelfPermission", X.04U, v4_2, v9_1, 1);
            } else {
                v11_2.postInvoke(0, 2908, "androidx/core/content/ContextCompat", "checkSelfPermission", X.04U, v4_2, v9_1, 0);
                v5_3 = ((Integer) v5_2.returnValue).intValue();
            }
            if (v5_3 == null) {
                if (this.LCC == null) {
                    this.LCC = android.accounts.AccountManager.get(this.LIIII.L);
                }
                try {
                    X.3Oo v4_13 = ((android.accounts.Account[]) X.3Rv.L(this.LCC, "com.google", new String[] {"service_HOSTED"}), "dzBzEgU1UM3QUBkgSxaWaaw9Bz14/yzxe1dYm0ZJPLqwOID9zPVdd3eEmUDB28GN").getResult());
                } catch (android.accounts.AccountManager v5_0) {
                    this.LIIII.ag_().LC.L("Exception checking account types", v5_0);
                    this.LB = v1_4;
                    this.L = Boolean.valueOf(0);
                    return 0;
                } catch (android.accounts.AccountManager v5_0) {
                } catch (android.accounts.AccountManager v5_0) {
                }
                if ((v4_13 == null) || (v4_13.length <= 0)) {
                    Boolean v3_18 = ((android.accounts.Account[]) X.3Rv.L(this.LCC, "com.google", new String[] {"service_uca"}), "dzBzEgU1UM3QUBkgSxaWaaw9Bz14/yzxe1dYm0ZJPLqwOID9zPVdd3eEmUDB28GN").getResult());
                    if ((v3_18 == null) || (v3_18.length <= 0)) {
                        this.LB = v1_4;
                        this.L = Boolean.valueOf(0);
                        return 0;
                    } else {
                        this.L = Boolean.valueOf(1);
                        this.LB = v1_4;
                        return 1;
                    }
                } else {
                    this.L = Boolean.valueOf(1);
                    this.LB = v1_4;
                    return 1;
                }
            } else {
                this.LIIII.ag_().LCI.L("Permission error checking for dasher/unicorn accounts");
                this.LB = v1_4;
                this.L = Boolean.valueOf(0);
                return 0;
            }
        }
    }

/**
X.3RZ;L(J)Z
*/

    private final boolean L(long p39)
    {
        void v1 = this;
        Object v0_7 = this.L;
        X.3RZ.L(v0_7);
        v0_7.LCCII();
        try {
            String v2_8 = new X.3RX(this);
            Object v0_69 = this.L;
            X.3RZ.L(v0_69);
            v0_69.L(p39, this.LIIJILLL, v2_8);
            Object v0_1 = v2_8.LBL;
        } catch (String v2_0) {
            Object v0_0 = v1.L;
            X.3RZ.L(v0_0);
            v0_0.LCI();
            throw v2_0;
        }
        if ((v0_1 == null) || (v0_1.isEmpty())) {
            Object v0_3 = this.L;
            X.3RZ.L(v0_3);
            v0_3.LF();
            Object v0_4 = this.L;
            X.3RZ.L(v0_4);
            v0_4.LCI();
            return 0;
        } else {
            Object v0_9 = ((X.3Iq) v2_8.L.LFFL());
            v0_9.LF();
            android.content.ContentValues v10_1 = 0;
            java.security.SecureRandom v20_0 = 0;
            int v25 = 0;
            String v22_0 = -1;
            long v24_0 = 0;
            X.3Rx v21_0 = -1;
            int v16 = 0;
            while (v10_1 < v2_8.LBL.size()) {
                android.database.sqlite.SQLiteException v5_53 = ((X.3Ie) ((X.3Ig) v2_8.LBL.get(v10_1)).LFFL());
                String v6_42 = this.LFF;
                X.3RZ.L(v6_42);
                if (!v6_42.LC(v2_8.L.zzv, v5_53.LCC())) {
                    if (v5_53.LCC().equals(X.3Po.L("_ai"))) {
                        v5_53.L("_ai");
                        this.ag_().LFFFF.L("Renaming ad_impression to _ai");
                        if (android.util.Log.isLoggable(this.ag_().LB(), 5)) {
                            String v6_0 = 0;
                            while (v6_0 < v5_53.L()) {
                                if (("ad_platform".equals(v5_53.LB(v6_0).zzf)) && ((!v5_53.LB(v6_0).zzg.isEmpty()) && ("admob".equalsIgnoreCase(v5_53.LB(v6_0).zzg)))) {
                                    this.ag_().LD.L("AdMob ad impression logged from app. Potentially duplicative.");
                                }
                                v6_0++;
                            }
                        }
                    }
                    String v6_1 = this.LFF;
                    X.3RZ.L(v6_1);
                    String v19_0 = v6_1.LBL(v2_8.L.zzv, v5_53.LCC());
                    if (v19_0 != null) {
                        String v6_3 = 0;
                        Boolean v18_0 = 0;
                        int v15_0 = 0;
                        while (v6_3 < v5_53.L()) {
                            if (!"_c".equals(v5_53.LB(v6_3).zzf)) {
                                if ("_r".equals(v5_53.LB(v6_3).zzf)) {
                                    String v7_6 = ((X.3Ij) v5_53.LB(v6_3).LFFL());
                                    v7_6.L(1);
                                    v5_53.L(v6_3, ((X.3Ik) v7_6.LIIL()));
                                    v15_0 = 1;
                                }
                            } else {
                                String v7_8 = ((X.3Ij) v5_53.LB(v6_3).LFFL());
                                v7_8.L(1);
                                v5_53.L(v6_3, ((X.3Ik) v7_8.LIIL()));
                                v18_0 = 1;
                            }
                            v6_3++;
                        }
                        if ((v18_0 == null) && (v19_0 != null)) {
                            this.ag_().LFFFF.L("Marking event as conversion", this.LCC.LF.L(v5_53.LCC()));
                            String v6_5 = X.3Ik.LB();
                            v6_5.L("_c");
                            v6_5.L(1);
                            v5_53.L(v6_5);
                        }
                        if (v15_0 == 0) {
                            this.ag_().LFFFF.L("Marking event as real-time", this.LCC.LF.L(v5_53.LCC()));
                            String v6_8 = X.3Ik.LB();
                            v6_8.L("_r");
                            v6_8.L(1);
                            v5_53.L(v6_8);
                        }
                        int v4_9 = this.L;
                        X.3RZ.L(v4_9);
                        if (v4_9.L(this.LI(), v2_8.L.zzv, 0, 1).LCC <= ((long) this.L().LB(v2_8.L.zzv, X.3Oc.LFLL))) {
                            v16 = 1;
                        } else {
                            X.3RZ.L(v5_53, "_r");
                        }
                        if (!X.3Rf.LCCII(v5_53.LCC())) {
                            if (v19_0 == null) {
                                if (!"_e".equals(v5_53.LCC())) {
                                    if ("_vs".equals(v5_53.LCC())) {
                                        X.3RZ.L(this.LFI);
                                        if (X.3Rb.L(((X.3Ig) v5_53.LIIL()), "_et") == null) {
                                            if ((v25 == 0) || (Math.abs((v25.LBL() - v5_53.LBL())) > 1000)) {
                                                v24_0 = v5_53;
                                                v21_0 = v20_0;
                                            } else {
                                                int v4_23 = ((X.3Ie) v25.LIIJJILLDILLLLLILLLLLLLLLLLLLLL());
                                                if (!this.L(v4_23, v5_53)) {
                                                    v24_0 = v5_53;
                                                    v21_0 = v20_0;
                                                } else {
                                                    v0_9.L(v22_0, v4_23);
                                                    v24_0 = 0;
                                                    v25 = 0;
                                                }
                                            }
                                        }
                                    }
                                } else {
                                    X.3RZ.L(this.LFI);
                                    if (X.3Rb.L(((X.3Ig) v5_53.LIIL()), "_fr") == null) {
                                        if ((v24_0 == 0) || (Math.abs((v24_0.LBL() - v5_53.LBL())) > 1000)) {
                                            v25 = v5_53;
                                            v22_0 = v20_0;
                                        } else {
                                            int v4_26 = ((X.3Ie) v24_0.LIIJJILLDILLLLLILLLLLLLLLLLLLLL());
                                            if (!this.L(v5_53, v4_26)) {
                                                v25 = v5_53;
                                                v22_0 = v20_0;
                                            } else {
                                                v0_9.L(v21_0, v4_26);
                                                v25 = 0;
                                                v24_0 = 0;
                                            }
                                        }
                                    }
                                }
                                v2_8.LBL.set(v10_1, ((X.3Ig) v5_53.LIIL()));
                                v20_0++;
                                v0_9.L(v5_53);
                                v10_1++;
                            } else {
                            }
                        } else {
                            if (v19_0 == null) {
                            } else {
                                int v4_12 = this.L;
                                X.3RZ.L(v4_12);
                                if (v4_12.L(this.LI(), v2_8.L.zzv, 1, 0).LBL > ((long) this.L().LB(v2_8.L.zzv, X.3Oc.LFI))) {
                                    this.ag_().LCCII.L("Too many conversions. Not logging as conversion. appId", X.3Or.L(v2_8.L.zzv));
                                    int v4_15 = 0;
                                    String v6_12 = 0;
                                    int v15_3 = 0;
                                    String v7_2 = -1;
                                    while (v6_12 < v5_53.L()) {
                                        String v8_6 = v5_53.LB(v6_12);
                                        if (!"_c".equals(v8_6.zzf)) {
                                            if ("_err".equals(v8_6.zzf)) {
                                                v15_3 = 1;
                                            }
                                        } else {
                                            v4_15 = ((X.3Ij) v8_6.LFFL());
                                            v7_2 = v6_12;
                                        }
                                        v6_12++;
                                    }
                                    if (v15_3 == 0) {
                                        if (v4_15 != 0) {
                                            String v6_14 = ((X.3Ij) v4_15.LIIJJILLDILLLLLILLLLLLLLLLLLLLL());
                                            v6_14.L("_err");
                                            v6_14.L(10);
                                            v5_53.L(v7_2, ((X.3Ik) v6_14.LIIL()));
                                            int v15_5 = new java.util.ArrayList(v5_53.LCCII());
                                            String v11_0 = 0;
                                            String v8_3 = -1;
                                            String v7_3 = -1;
                                            while (v11_0 < v15_5.size()) {
                                                if (!"value".equals(((X.3Ik) v15_5.get(v11_0)).zzf)) {
                                                    if ("currency".equals(((X.3Ik) v15_5.get(v11_0)).zzf)) {
                                                        v7_3 = v11_0;
                                                    }
                                                } else {
                                                    v8_3 = v11_0;
                                                }
                                                v11_0++;
                                            }
                                            if (v8_3 != -1) {
                                                if ((((X.3Ik) v15_5.get(v8_3)).LCC()) || (((X.3Ik) v15_5.get(v8_3)).LC())) {
                                                    if (v7_3 != -1) {
                                                        String v7_4 = ((X.3Ik) v15_5.get(v7_3)).zzg;
                                                        if (v7_4.length() == 3) {
                                                            int v4_19 = 0;
                                                            while (v4_19 < v7_4.length()) {
                                                                String v11_1 = v7_4.codePointAt(v4_19);
                                                                if (Character.isLetter(v11_1)) {
                                                                    v4_19 += Character.charCount(v11_1);
                                                                }
                                                            }
                                                        }
                                                    }
                                                    this.ag_().LD.L("Value parameter discarded. You must also supply a 3-letter ISO_4217 currency code in the currency parameter.");
                                                    v5_53.L(v8_3);
                                                    X.3RZ.L(v5_53, "_c");
                                                    X.3RZ.L(v5_53, 19, "currency");
                                                } else {
                                                    this.ag_().LD.L("Value must be specified with a numeric type.");
                                                    v5_53.L(v8_3);
                                                    X.3RZ.L(v5_53, "_c");
                                                    X.3RZ.L(v5_53, 18, "value");
                                                }
                                            }
                                        }
                                    } else {
                                        if (v4_15 != 0) {
                                            v5_53.L(v7_2);
                                        }
                                    }
                                    this.ag_().LBL.L("Did not find conversion parameter. appId", X.3Or.L(v2_8.L.zzv));
                                }
                            }
                        }
                    } else {
                        X.3RZ.L(this.LFI);
                        int v4_6 = v5_53.LCC();
                        X.3D5.L(v4_6);
                        String v6_2 = v4_6.hashCode();
                        if (v6_2 == 94660) {
                            if (v4_6.equals("_in")) {
                            }
                        } else {
                            if (v6_2 == 95025) {
                                if (v4_6.equals("_ug")) {
                                }
                            } else {
                                if ((v6_2 == 95027) && (v4_6.equals("_ui"))) {
                                }
                            }
                        }
                    }
                } else {
                    this.ag_().LCCII.L("Dropping blocked raw event. appId", X.3Or.L(v2_8.L.zzv), this.LCC.LF.L(v5_53.LCC()));
                    int v4_33 = this.LFF;
                    X.3RZ.L(v4_33);
                    if (!v4_33.LCCII(v2_8.L.zzv)) {
                        int v4_34 = this.LFF;
                        X.3RZ.L(v4_34);
                        if ((!v4_34.LCI(v2_8.L.zzv)) && (!"_err".equals(v5_53.LCC()))) {
                            this.LFFFF();
                            X.3Rf.L(this.LIILIIL, v2_8.L.zzv, 11, "_ev", v5_53.LCC(), 0);
                        }
                    }
                }
            }
            X.3Rx v3_260 = 0;
            String v7_15 = 0;
            while (v7_15 < v20_0) {
                String v6_38 = v0_9.L(v7_15);
                if (!"_e".equals(v6_38.zzg)) {
                    X.3RZ.L(this.LFI);
                    String v6_40 = X.3Rb.L(v6_38, "_et");
                    if ((v6_40 != null) && (v6_40.LCC())) {
                        String v6_41 = Long.valueOf(v6_40.zzh);
                        if ((v6_41 != null) && (v6_41.longValue() > 0)) {
                            v3_260 += v6_41.longValue();
                        }
                    }
                } else {
                    X.3RZ.L(this.LFI);
                    if (X.3Rb.L(v6_38, "_fr") == null) {
                    } else {
                        if (v0_9.LB) {
                            v0_9.LIILIIL();
                            v0_9.LB = 0;
                        }
                        android.database.sqlite.SQLiteException v5_50 = ((X.3Ir) v0_9.L);
                        v5_50.LB();
                        v5_50.zzi.remove(v7_15);
                        v20_0--;
                        v7_15--;
                    }
                }
                v7_15++;
            }
            v1 = this.L(v0_9, v3_260, 0);
            String v8_17 = v0_9.LIIIL().iterator();
            while (v8_17.hasNext()) {
                if ("_s".equals(((X.3Ig) v8_17.next()).zzg)) {
                    String v6_35 = v1.L;
                    X.3RZ.L(v6_35);
                    v6_35.LCC(v0_9.LIIIIZ(), "_se");
                    break;
                }
            }
            if (X.3Rb.L(v0_9, "_sid") < 0) {
                X.3Rx v3_314 = X.3Rb.L(v0_9, "_se");
                if (v3_314 >= null) {
                    v0_9.LBL(v3_314);
                    v1.ag_().LBL.L("Session engagement user property is in the bundle without session ID. appId", X.3Or.L(v2_8.L.zzv));
                }
            } else {
                v1 = v1.L(v0_9, v3_260, 1);
            }
            String v6_39 = v1.LFI;
            X.3RZ.L(v6_39);
            v6_39.LIIII.ag_().LFFFF.L("Checking account type status for ad personalization signals");
            int v4_5 = v6_39.LFF.LFF;
            X.3RZ.L(v4_5);
            if (v4_5.LC(v0_9.LIIIIZ())) {
                int v4_10 = v6_39.LFF.L;
                X.3RZ.L(v4_10);
                X.3Rx v3_59 = v4_10.LC(v0_9.LIIIIZ());
                if ((v3_59 != null) && ((v3_59.LIIIIZZ()) && (v6_39.LIIII.LCC().LBL()))) {
                    v6_39.LIIII.ag_().LFF.L("Turning off ad personalization due to account type");
                    android.database.sqlite.SQLiteException v5_1 = X.3J0.L();
                    v5_1.L("_npa");
                    X.3Rx v3_141 = v6_39.LIIII.LCC();
                    v3_141.ac_();
                    v5_1.LB(v3_141.LB);
                    v5_1.L(1);
                    String v6_26 = ((X.3J0) v5_1.LIIL());
                    android.database.sqlite.SQLiteException v5_3 = 0;
                    while (v5_3 < v0_9.LB()) {
                        if (!"_npa".equals(v0_9.LD(v5_3).zzg)) {
                            v5_3++;
                        } else {
                            v0_9.L(v5_3, v6_26);
                        }
                    }
                    v0_9.L(v6_26);
                }
            }
            v0_9.LF(9223372036854775807);
            v0_9.LCC(-9223372036854775808);
            String v8_9 = 0;
            while (v8_9 < v0_9.L()) {
                Long v9_17 = v0_9.L(v8_9);
                if (v9_17.zzh < v0_9.LC()) {
                    v0_9.LF(v9_17.zzh);
                }
                if (v9_17.zzh > v0_9.LBL()) {
                    v0_9.LCC(v9_17.zzh);
                }
                v8_9++;
            }
            if (v0_9.LB) {
                v0_9.LIILIIL();
                v0_9.LB = 0;
            }
            android.database.sqlite.SQLiteException v5_5 = ((X.3Ir) v0_9.L);
            v5_5.zzf = (v5_5.zzf & -268435457);
            v5_5.zzM = X.3Ir.zze.zzM;
            if (v0_9.LB) {
                v0_9.LIILIIL();
                v0_9.LB = 0;
            }
            ((X.3Ir) v0_9.L).zzH = X.3Kx.L;
            android.database.sqlite.SQLiteException v5_6 = v1.LB;
            X.3RZ.L(v5_6);
            v0_9.L(v5_6.L(v0_9.LIIIIZ(), v0_9.LIIIL(), v0_9.LIIILL(), Long.valueOf(v0_9.LC()), Long.valueOf(v0_9.LBL())));
            if ("1".equals(v1.L().L.L(v2_8.L.zzv, "measurement.event_sampling_enabled"))) {
                String v7_13 = new java.util.HashMap();
                String v6_31 = new java.util.ArrayList();
                java.security.SecureRandom v20_1 = v1.LFFFF().LICI();
                int v17_1 = 0;
                while (v17_1 < v0_9.L()) {
                    android.database.sqlite.SQLiteException v5_27 = ((X.3Ie) v0_9.L(v17_1).LFFL());
                    if (!v5_27.LCC().equals("_ep")) {
                        String v8_19;
                        String v8_18 = v1.LFF;
                        X.3RZ.L(v8_18);
                        android.content.ContentValues v10_13 = v2_8.L.zzv;
                        int v4_67 = v8_18.L(v10_13, "measurement.account.time_zone_offset_minutes");
                        if (android.text.TextUtils.isEmpty(v4_67)) {
                            v8_19 = 0;
                        } else {
                            try {
                                v8_19 = Long.parseLong(v4_67);
                            } catch (Long v9_11) {
                                v8_19.LIIII.ag_().LCCII.L("Unable to parse timezone offset. appId", X.3Or.L(v10_13), v9_11);
                            }
                        }
                        int v4_74;
                        v1.LFFFF();
                        android.content.ContentValues v10_14 = X.3Rf.L(v5_27.LBL(), v8_19);
                        X.3Rx v3_285 = ((X.3Ig) v5_27.LIIL());
                        String v12_4 = Long.valueOf(1);
                        if (android.text.TextUtils.isEmpty("_dbg")) {
                            X.3Rx v3_293 = v1.LFF;
                            X.3RZ.L(v3_293);
                            String v12_5 = v2_8.L.zzv;
                            int v4_73 = v5_27.LCC();
                            v3_293.ac_();
                            X.3PI.LFI(v3_293, v12_5);
                            X.3Rx v3_296 = ((java.util.Map) v3_293.LFFFF.get(v12_5));
                            if (v3_296 == null) {
                                v4_74 = 1;
                            } else {
                                X.3Rx v3_298 = ((Integer) v3_296.get(v4_73));
                                if (v3_298 != null) {
                                    v4_74 = v3_298.intValue();
                                    if (v4_74 <= 0) {
                                        v1.ag_().LCCII.L("Sample rate must be positive. event, rate", v5_27.LCC(), Integer.valueOf(v4_74));
                                        v6_31.add(((X.3Ig) v5_27.LIIL()));
                                        v0_9.L(v17_1, v5_27);
                                        v17_1++;
                                    }
                                } else {
                                    v4_74 = 1;
                                }
                            }
                        } else {
                            X.3Oo v14_2 = v3_285.zzf.iterator();
                            while (v14_2.hasNext()) {
                                int v4_71 = ((X.3Ik) v14_2.next());
                                if ("_dbg".equals(v4_71.zzf)) {
                                    if (!v12_4.equals(Long.valueOf(v4_71.zzh))) {
                                        break;
                                    }
                                    v4_74 = 1;
                                }
                            }
                        }
                        X.3Rx v3_306 = ((X.3Rx) v7_13.get(v5_27.LCC()));
                        if (v3_306 == null) {
                            long v13_3 = v1.L;
                            X.3RZ.L(v13_3);
                            v3_306 = v13_3.LBL(v2_8.L.zzv, v5_27.LCC());
                            if (v3_306 == null) {
                                v1.ag_().LCCII.L("Event being bundled has no eventAggregate. appId, eventName", v2_8.L.zzv, v5_27.LCC());
                                v3_306 = new X.3Rx;
                                v3_306(v2_8.L.zzv, v5_27.LCC(), 1, 1, 1, v5_27.LBL(), 0, 0, 0, 0, 0);
                            }
                        }
                        X.3RZ.L(v1.LFI);
                        String v12_12 = ((Long) X.3Rb.LB(((X.3Ig) v5_27.LIIL()), "_eid"));
                        Boolean v18_1 = Boolean.valueOf((v12_12 instanceof Object));
                        if (v4_74 != 1) {
                            if (v20_1.nextInt(v4_74) != 0) {
                                long v13_15;
                                long v13_11 = v3_306.LD;
                                if (v13_11 == 0) {
                                    v1.LFFFF();
                                    v13_15 = X.3Rf.L(((X.3Ig) v5_27.L).zzi, v8_19);
                                } else {
                                    v13_15 = v13_11.longValue();
                                }
                                if (v13_15 == v10_14) {
                                    if (v18_1.booleanValue()) {
                                        v7_13.put(v5_27.LCC(), v3_306.L(v12_12, 0, 0));
                                    }
                                } else {
                                    X.3RZ.L(v1.LFI);
                                    X.3Rb.L(v5_27, "_efs", Long.valueOf(1));
                                    X.3RZ.L(v1.LFI);
                                    Long v9_14 = Long.valueOf(((long) v4_74));
                                    X.3Rb.L(v5_27, "_sr", v9_14);
                                    v6_31.add(((X.3Ig) v5_27.LIIL()));
                                    if (v18_1.booleanValue()) {
                                        v3_306 = v3_306.L(0, v9_14, Boolean.valueOf(1));
                                    }
                                    v7_13.put(v5_27.LCC(), v3_306.L(v5_27.LBL(), v10_14));
                                }
                            } else {
                                X.3RZ.L(v1.LFI);
                                String v8_32 = Long.valueOf(((long) v4_74));
                                X.3Rb.L(v5_27, "_sr", v8_32);
                                v6_31.add(((X.3Ig) v5_27.LIIL()));
                                if (v18_1.booleanValue()) {
                                    v3_306 = v3_306.L(0, v8_32, 0);
                                }
                                v7_13.put(v5_27.LCC(), v3_306.L(v5_27.LBL(), v10_14));
                            }
                            v0_9.L(v17_1, v5_27);
                        } else {
                            v6_31.add(((X.3Ig) v5_27.LIIL()));
                            if ((v18_1.booleanValue()) && ((v3_306.LF != null) || ((v3_306.LFF != null) || (v3_306.LFFFF != null)))) {
                                v7_13.put(v5_27.LCC(), v3_306.L(0, 0, 0));
                            }
                            v0_9.L(v17_1, v5_27);
                        }
                    } else {
                        X.3RZ.L(v1.LFI);
                        Long v9_16 = ((String) X.3Rb.LB(((X.3Ig) v5_27.LIIL()), "_en"));
                        int v4_100 = ((X.3Rx) v7_13.get(v9_16));
                        if (v4_100 != 0) {
                            if (v4_100.LF == null) {
                                X.3Rx v3_328 = v4_100.LFF;
                                if ((v3_328 != null) && (v3_328.longValue() > 1)) {
                                    X.3RZ.L(v1.LFI);
                                    X.3Rb.L(v5_27, "_sr", v4_100.LFF);
                                }
                                X.3Rx v3_332 = v4_100.LFFFF;
                                if ((v3_332 != null) && (v3_332.booleanValue())) {
                                    X.3RZ.L(v1.LFI);
                                    X.3Rb.L(v5_27, "_efs", Long.valueOf(1));
                                }
                                v6_31.add(((X.3Ig) v5_27.LIIL()));
                            }
                        } else {
                            String v8_34 = v1.L;
                            X.3RZ.L(v8_34);
                            int v4_101 = v2_8.L.zzv;
                            java.util.Objects.requireNonNull(v9_16, "null reference");
                            v4_100 = v8_34.LBL(v4_101, v9_16);
                            if (v4_100 != 0) {
                                v7_13.put(v9_16, v4_100);
                            }
                        }
                        v0_9.L(v17_1, v5_27);
                    }
                }
                if (v6_31.size() < v0_9.L()) {
                    v0_9.LF();
                    if (v0_9.LB) {
                        v0_9.LIILIIL();
                        v0_9.LB = 0;
                    }
                    X.3Rx v3_205 = ((X.3Ir) v0_9.L);
                    v3_205.LB();
                    X.3I3.L(v6_31, v3_205.zzi);
                }
                android.database.sqlite.SQLiteException v5_8 = v7_13.entrySet().iterator();
                while (v5_8.hasNext()) {
                    X.3Rx v3_270 = ((java.util.Map$Entry) v5_8.next());
                    int v4_65 = v1.L;
                    X.3RZ.L(v4_65);
                    v4_65.L(((X.3Rx) v3_270.getValue()));
                }
            }
            String v7_14 = v2_8.L.zzv;
            X.3Rx v3_210 = v1.L;
            X.3RZ.L(v3_210);
            String v8_11 = v3_210.LC(v7_14);
            if (v8_11 != null) {
                if (v0_9.L() > 0) {
                    X.3Rx v3_212 = v8_11.LD();
                    if (v3_212 == 0) {
                        if (v0_9.LB) {
                            v0_9.LIILIIL();
                            v0_9.LB = 0;
                        }
                        android.content.ContentValues v10_4 = ((X.3Ir) v0_9.L);
                        v10_4.zzf = (v10_4.zzf & -33);
                        v10_4.zzo = 0;
                    } else {
                        v0_9.LCI(v3_212);
                    }
                    android.content.ContentValues v10_5 = v8_11.LFF();
                    if (v10_5 != 0) {
                        v3_212 = v10_5;
                    }
                    if (v3_212 == 0) {
                        if (v0_9.LB) {
                            v0_9.LIILIIL();
                            v0_9.LB = 0;
                        }
                        int v4_47 = ((X.3Ir) v0_9.L);
                        v4_47.zzf = (v4_47.zzf & -17);
                        v4_47.zzn = 0;
                    } else {
                        v0_9.LD(v3_212);
                    }
                    v8_11.LIIIIZ();
                    v0_9.LCC(((int) v8_11.LF()));
                    v8_11.LF(v0_9.LC());
                    v8_11.LCI(v0_9.LBL());
                    v8_11.L.ah_().ac_();
                    String v6_32 = v8_11.LD;
                    v8_11.LCI(0);
                    if (v6_32 == null) {
                        if (v0_9.LB) {
                            v0_9.LIILIIL();
                            v0_9.LB = 0;
                        }
                        android.database.sqlite.SQLiteException v5_13 = ((X.3Ir) v0_9.L);
                        v5_13.zzf = (v5_13.zzf & -2097153);
                        v5_13.zzE = X.3Ir.zze.zzE;
                    } else {
                        if (v0_9.LB) {
                            v0_9.LIILIIL();
                            v0_9.LB = 0;
                        }
                        android.database.sqlite.SQLiteException v5_15 = ((X.3Ir) v0_9.L);
                        v5_15.zzf = (v5_15.zzf | 2097152);
                        v5_15.zzE = v6_32;
                    }
                    X.3Rx v3_231 = v1.L;
                    X.3RZ.L(v3_231);
                    v3_231.L(v8_11);
                }
            } else {
                v1.ag_().LBL.L("Bundling raw events w/o app info. appId", X.3Or.L(v2_8.L.zzv));
            }
            if (v0_9.L() > 0) {
                int v4_53 = v1.LFF;
                X.3RZ.L(v4_53);
                int v4_54 = v4_53.L(v2_8.L.zzv);
                if ((v4_54 == 0) || (!v4_54.LBL())) {
                    if (!v2_8.L.zzF.isEmpty()) {
                        v1.ag_().LCCII.L("Did not find measurement config or missing version info. appId", X.3Or.L(v2_8.L.zzv));
                    } else {
                        v0_9.LB(-1);
                    }
                } else {
                    v0_9.LB(v4_54.zzf);
                }
                Long v9_10 = v1.L;
                X.3RZ.L(v9_10);
                String v8_14 = ((X.3Ir) v0_9.LIIL());
                v9_10.ac_();
                v9_10.LFFLLL();
                X.3D5.L(v8_14);
                X.3D5.L(v8_14.zzv);
                X.3D5.LB(v8_14.LC());
                v9_10.LD();
                X.3Oo v14_0 = v9_10.LIIII.LFF.L();
                if ((v8_14.zzm < (v14_0 - X.3Pl.LF())) || (v8_14.zzm > (X.3Pl.LF() + v14_0))) {
                    v9_10.LIIII.ag_().LCCII.L("Storing bundle outside of the max uploading time span. appId, now, timestamp", X.3Or.L(v8_14.zzv), Long.valueOf(v14_0), Long.valueOf(v8_14.zzm));
                }
                X.3Rx v3_253 = v8_14.LF();
                Object v0_21 = v9_10.LFF.LFI;
                X.3RZ.L(v0_21);
                String v12_2 = v0_21.LB(v3_253);
                v9_10.LIIII.ag_().LFFFF.L("Saving bundle, size", Integer.valueOf(v12_2.length));
                android.content.ContentValues v10_11 = new android.content.ContentValues();
                v10_11.put("app_id", v8_14.zzv);
                v10_11.put("bundle_end_timestamp", Long.valueOf(v8_14.zzm));
                v10_11.put("data", v12_2);
                v10_11.put("has_realtime", Integer.valueOf(v16));
                if (v8_14.LCC()) {
                    v10_11.put("retry_count", Integer.valueOf(v8_14.zzR));
                }
                try {
                    if (v9_10.LC().insert("queue", 0, v10_11) == -1) {
                        v9_10.LIIII.ag_().LBL.L("Failed to insert bundle (got -1). appId", X.3Or.L(v8_14.zzv));
                    }
                } catch (android.database.sqlite.SQLiteException v5_19) {
                    v9_10.LIIII.ag_().LBL.L("Error storing bundle. appId", X.3Or.L(v8_14.zzv), v5_19);
                }
            }
            String v6_33 = v1.L;
            X.3RZ.L(v6_33);
            android.database.sqlite.SQLiteException v5_21 = v2_8.LB;
            X.3D5.L(v5_21);
            v6_33.ac_();
            v6_33.LFFLLL();
            String v8_16 = new StringBuilder("rowid in (");
            int v4_61 = 0;
            while (v4_61 < v5_21.size()) {
                if (v4_61 != 0) {
                    v8_16.append(",");
                }
                v8_16.append(((Long) v5_21.get(v4_61)).longValue());
                v4_61++;
            }
            v8_16.append(")");
            String v2_2 = v6_33.LC().delete("raw_events", v8_16.toString(), 0);
            if (v2_2 != v5_21.size()) {
                v6_33.LIIII.ag_().LBL.L("Deleted fewer rows from raw events table than expected", Integer.valueOf(v2_2), Integer.valueOf(v5_21.size()));
            }
            android.database.sqlite.SQLiteException v5_23 = v1.L;
            X.3RZ.L(v5_23);
            X.3Rx v3_267 = v5_23.LC();
            try {
                String v2_4 = new String[2];
                v2_4[0] = v7_14;
                v2_4[1] = v7_14;
                v3_267.execSQL("delete from raw_events_metadata where app_id=? and metadata_fingerprint not in (select distinct metadata_fingerprint from raw_events where app_id=?)", v2_4);
            } catch (int v4_64) {
                v5_23.LIIII.ag_().LBL.L("Failed to remove unused event metadata. appId", X.3Or.L(v7_14), v4_64);
            }
            Object v0_63 = v1.L;
            X.3RZ.L(v0_63);
            v0_63.LF();
            Object v0_64 = v1.L;
            X.3RZ.L(v0_64);
            v0_64.LCI();
            return 1;
        }
    }


}