PGDMP                      |         	   brieflydb    16.4    16.4 ,    =           0    0    ENCODING    ENCODING     #   SET client_encoding = 'SQL_ASCII';
                      false            >           0    0 
   STDSTRINGS 
   STDSTRINGS     (   SET standard_conforming_strings = 'on';
                      false            ?           0    0 
   SEARCHPATH 
   SEARCHPATH     8   SELECT pg_catalog.set_config('search_path', '', false);
                      false            @           1262    16429 	   brieflydb    DATABASE     u   CREATE DATABASE brieflydb WITH TEMPLATE = template0 ENCODING = 'UTF8' LOCALE_PROVIDER = libc LOCALE = 'en_US.UTF-8';
    DROP DATABASE brieflydb;
                doadmin    false            A           0    0    SCHEMA public    ACL     )   GRANT CREATE ON SCHEMA public TO server;
                   pg_database_owner    false    5            �            1259    16554    News    TABLE     �   CREATE TABLE public."News" (
    id integer NOT NULL,
    link character varying(255) NOT NULL,
    created_at timestamp with time zone NOT NULL,
    topic_id integer NOT NULL
);
    DROP TABLE public."News";
       public         heap    server    false            �            1259    16553    News_id_seq    SEQUENCE     �   CREATE SEQUENCE public."News_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 $   DROP SEQUENCE public."News_id_seq";
       public          server    false    222            B           0    0    News_id_seq    SEQUENCE OWNED BY     ?   ALTER SEQUENCE public."News_id_seq" OWNED BY public."News".id;
          public          server    false    221            �            1259    16565    Profiles    TABLE     �   CREATE TABLE public."Profiles" (
    id integer NOT NULL,
    user_id bigint NOT NULL,
    mode bigint DEFAULT 0 NOT NULL,
    text_format_id bigint NOT NULL,
    is_completed boolean DEFAULT false NOT NULL
);
    DROP TABLE public."Profiles";
       public         heap    server    false            �            1259    16564    Profiles_id_seq    SEQUENCE     �   CREATE SEQUENCE public."Profiles_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 (   DROP SEQUENCE public."Profiles_id_seq";
       public          server    false    224            C           0    0    Profiles_id_seq    SEQUENCE OWNED BY     G   ALTER SEQUENCE public."Profiles_id_seq" OWNED BY public."Profiles".id;
          public          server    false    223            �            1259    16545    Text_Formats    TABLE     j   CREATE TABLE public."Text_Formats" (
    id integer NOT NULL,
    name character varying(255) NOT NULL
);
 "   DROP TABLE public."Text_Formats";
       public         heap    server    false            �            1259    16544    Text_Formats_id_seq    SEQUENCE     �   CREATE SEQUENCE public."Text_Formats_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 ,   DROP SEQUENCE public."Text_Formats_id_seq";
       public          server    false    220            D           0    0    Text_Formats_id_seq    SEQUENCE OWNED BY     O   ALTER SEQUENCE public."Text_Formats_id_seq" OWNED BY public."Text_Formats".id;
          public          server    false    219            �            1259    16536    Topics    TABLE     r   CREATE TABLE public."Topics" (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    url text
);
    DROP TABLE public."Topics";
       public         heap    server    false            �            1259    16599    Topics_Profiles    TABLE     �   CREATE TABLE public."Topics_Profiles" (
    id integer NOT NULL,
    profile_id bigint NOT NULL,
    topic_id bigint NOT NULL
);
 %   DROP TABLE public."Topics_Profiles";
       public         heap    server    false            �            1259    16598    Topics_Profiles_id_seq    SEQUENCE     �   CREATE SEQUENCE public."Topics_Profiles_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 /   DROP SEQUENCE public."Topics_Profiles_id_seq";
       public          server    false    226            E           0    0    Topics_Profiles_id_seq    SEQUENCE OWNED BY     U   ALTER SEQUENCE public."Topics_Profiles_id_seq" OWNED BY public."Topics_Profiles".id;
          public          server    false    225            �            1259    16535    Topics_id_seq    SEQUENCE     �   CREATE SEQUENCE public."Topics_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 &   DROP SEQUENCE public."Topics_id_seq";
       public          server    false    218            F           0    0    Topics_id_seq    SEQUENCE OWNED BY     C   ALTER SEQUENCE public."Topics_id_seq" OWNED BY public."Topics".id;
          public          server    false    217            �            1259    16525    Users    TABLE     �   CREATE TABLE public."Users" (
    id integer NOT NULL,
    first_name character varying(255),
    last_name character varying(255),
    username character varying(255),
    chat_id bigint NOT NULL,
    created_at timestamp with time zone NOT NULL
);
    DROP TABLE public."Users";
       public         heap    server    false            �            1259    16524    Users_id_seq    SEQUENCE     �   CREATE SEQUENCE public."Users_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 %   DROP SEQUENCE public."Users_id_seq";
       public          server    false    216            G           0    0    Users_id_seq    SEQUENCE OWNED BY     A   ALTER SEQUENCE public."Users_id_seq" OWNED BY public."Users".id;
          public          server    false    215            �           2604    16557    News id    DEFAULT     f   ALTER TABLE ONLY public."News" ALTER COLUMN id SET DEFAULT nextval('public."News_id_seq"'::regclass);
 8   ALTER TABLE public."News" ALTER COLUMN id DROP DEFAULT;
       public          server    false    221    222    222            �           2604    16568    Profiles id    DEFAULT     n   ALTER TABLE ONLY public."Profiles" ALTER COLUMN id SET DEFAULT nextval('public."Profiles_id_seq"'::regclass);
 <   ALTER TABLE public."Profiles" ALTER COLUMN id DROP DEFAULT;
       public          server    false    224    223    224            �           2604    16548    Text_Formats id    DEFAULT     v   ALTER TABLE ONLY public."Text_Formats" ALTER COLUMN id SET DEFAULT nextval('public."Text_Formats_id_seq"'::regclass);
 @   ALTER TABLE public."Text_Formats" ALTER COLUMN id DROP DEFAULT;
       public          server    false    220    219    220            �           2604    16539 	   Topics id    DEFAULT     j   ALTER TABLE ONLY public."Topics" ALTER COLUMN id SET DEFAULT nextval('public."Topics_id_seq"'::regclass);
 :   ALTER TABLE public."Topics" ALTER COLUMN id DROP DEFAULT;
       public          server    false    217    218    218            �           2604    16602    Topics_Profiles id    DEFAULT     |   ALTER TABLE ONLY public."Topics_Profiles" ALTER COLUMN id SET DEFAULT nextval('public."Topics_Profiles_id_seq"'::regclass);
 C   ALTER TABLE public."Topics_Profiles" ALTER COLUMN id DROP DEFAULT;
       public          server    false    226    225    226            �           2604    16528    Users id    DEFAULT     h   ALTER TABLE ONLY public."Users" ALTER COLUMN id SET DEFAULT nextval('public."Users_id_seq"'::regclass);
 9   ALTER TABLE public."Users" ALTER COLUMN id DROP DEFAULT;
       public          server    false    215    216    216            �           2606    16563    News News_link_key 
   CONSTRAINT     Q   ALTER TABLE ONLY public."News"
    ADD CONSTRAINT "News_link_key" UNIQUE (link);
 @   ALTER TABLE ONLY public."News" DROP CONSTRAINT "News_link_key";
       public            server    false    222            �           2606    16561    News News_pkey 
   CONSTRAINT     P   ALTER TABLE ONLY public."News"
    ADD CONSTRAINT "News_pkey" PRIMARY KEY (id);
 <   ALTER TABLE ONLY public."News" DROP CONSTRAINT "News_pkey";
       public            server    false    222            �           2606    16570    Profiles Profiles_pkey 
   CONSTRAINT     X   ALTER TABLE ONLY public."Profiles"
    ADD CONSTRAINT "Profiles_pkey" PRIMARY KEY (id);
 D   ALTER TABLE ONLY public."Profiles" DROP CONSTRAINT "Profiles_pkey";
       public            server    false    224            �           2606    16552 "   Text_Formats Text_Formats_name_key 
   CONSTRAINT     a   ALTER TABLE ONLY public."Text_Formats"
    ADD CONSTRAINT "Text_Formats_name_key" UNIQUE (name);
 P   ALTER TABLE ONLY public."Text_Formats" DROP CONSTRAINT "Text_Formats_name_key";
       public            server    false    220            �           2606    16550    Text_Formats Text_Formats_pkey 
   CONSTRAINT     `   ALTER TABLE ONLY public."Text_Formats"
    ADD CONSTRAINT "Text_Formats_pkey" PRIMARY KEY (id);
 L   ALTER TABLE ONLY public."Text_Formats" DROP CONSTRAINT "Text_Formats_pkey";
       public            server    false    220            �           2606    16604 $   Topics_Profiles Topics_Profiles_pkey 
   CONSTRAINT     f   ALTER TABLE ONLY public."Topics_Profiles"
    ADD CONSTRAINT "Topics_Profiles_pkey" PRIMARY KEY (id);
 R   ALTER TABLE ONLY public."Topics_Profiles" DROP CONSTRAINT "Topics_Profiles_pkey";
       public            server    false    226            �           2606    16543    Topics Topics_name_key 
   CONSTRAINT     U   ALTER TABLE ONLY public."Topics"
    ADD CONSTRAINT "Topics_name_key" UNIQUE (name);
 D   ALTER TABLE ONLY public."Topics" DROP CONSTRAINT "Topics_name_key";
       public            server    false    218            �           2606    16541    Topics Topics_pkey 
   CONSTRAINT     T   ALTER TABLE ONLY public."Topics"
    ADD CONSTRAINT "Topics_pkey" PRIMARY KEY (id);
 @   ALTER TABLE ONLY public."Topics" DROP CONSTRAINT "Topics_pkey";
       public            server    false    218            �           2606    16617    Users Users_chat_id_key 
   CONSTRAINT     Y   ALTER TABLE ONLY public."Users"
    ADD CONSTRAINT "Users_chat_id_key" UNIQUE (chat_id);
 E   ALTER TABLE ONLY public."Users" DROP CONSTRAINT "Users_chat_id_key";
       public            server    false    216            �           2606    16532    Users Users_pkey 
   CONSTRAINT     R   ALTER TABLE ONLY public."Users"
    ADD CONSTRAINT "Users_pkey" PRIMARY KEY (id);
 >   ALTER TABLE ONLY public."Users" DROP CONSTRAINT "Users_pkey";
       public            server    false    216            �           2606    16576 %   Profiles Profiles_text_format_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public."Profiles"
    ADD CONSTRAINT "Profiles_text_format_id_fkey" FOREIGN KEY (text_format_id) REFERENCES public."Text_Formats"(id);
 S   ALTER TABLE ONLY public."Profiles" DROP CONSTRAINT "Profiles_text_format_id_fkey";
       public          server    false    4255    220    224            �           2606    16571    Profiles Profiles_user_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public."Profiles"
    ADD CONSTRAINT "Profiles_user_id_fkey" FOREIGN KEY (user_id) REFERENCES public."Users"(id);
 L   ALTER TABLE ONLY public."Profiles" DROP CONSTRAINT "Profiles_user_id_fkey";
       public          server    false    224    216    4247            �           2606    16605 /   Topics_Profiles Topics_Profiles_profile_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public."Topics_Profiles"
    ADD CONSTRAINT "Topics_Profiles_profile_id_fkey" FOREIGN KEY (profile_id) REFERENCES public."Profiles"(id);
 ]   ALTER TABLE ONLY public."Topics_Profiles" DROP CONSTRAINT "Topics_Profiles_profile_id_fkey";
       public          server    false    4261    226    224            �           2606    16610 -   Topics_Profiles Topics_Profiles_topic_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public."Topics_Profiles"
    ADD CONSTRAINT "Topics_Profiles_topic_id_fkey" FOREIGN KEY (topic_id) REFERENCES public."Topics"(id);
 [   ALTER TABLE ONLY public."Topics_Profiles" DROP CONSTRAINT "Topics_Profiles_topic_id_fkey";
       public          server    false    226    218    4251                       826    16432    DEFAULT PRIVILEGES FOR TABLES    DEFAULT ACL     k   ALTER DEFAULT PRIVILEGES FOR ROLE doadmin IN SCHEMA public GRANT SELECT,INSERT,UPDATE ON TABLES TO server;
          public          doadmin    false           