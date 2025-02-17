# coding: utf-8
from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    text,
    Boolean,
)
from sqlalchemy.dialects.mysql import ENUM, TINYINT, VARCHAR
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class Asset(Base):
    __tablename__ = "assets"

    id = Column(Integer, primary_key=True)
    title = Column(VARCHAR(255), nullable=False)
    slug = Column(VARCHAR(255), nullable=False)
    created_at = Column(
        DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
    )
    description = Column(VARCHAR(255))
    external_id = Column(
        VARCHAR(255), comment="For integration and sync with external sources"
    )
    is_shareable = Column(TINYINT, nullable=False, server_default=text("'1'"))
    is_downloadable = Column(TINYINT, nullable=False, server_default=text("'1'"))
    thumbnail_url = Column(VARCHAR(2083), nullable=False)
    expires_at = Column(DateTime)
    activate_at = Column(DateTime)
    is_deleted = Column(TINYINT, nullable=False, server_default=text("'0'"))
    deleted_at = Column(DateTime)
    deleted_by = Column(Integer, nullable=True)
    created_by = Column(Integer, nullable=False)
    client_id = Column(
        Integer,
        comment="The Site ID or Client ID might not be required for Board features, but it is required for CRM features",
    )
    asset_type = Column(ENUM("LINK", "DOCUMENT", "IMAGE", "VIDEO"))


class Document(Asset):
    __tablename__ = "documents"

    id = Column(
        ForeignKey("assets.id", ondelete="CASCADE", onupdate="CASCADE"),
        primary_key=True,
    )
    size = Column(BigInteger, server_default=text("'0'"))
    extension = Column(VARCHAR(10), nullable=False)
    preview_url = Column(VARCHAR(2083), nullable=False)
    download_url = Column(VARCHAR(2083), nullable=False)
    page_count = Column(Integer, server_default=text("'0'"))
    width = Column(Integer, server_default=text("'0'"))
    height = Column(Integer, server_default=text("'0'"))


class Image(Asset):
    __tablename__ = "images"

    id = Column(
        ForeignKey("assets.id", ondelete="CASCADE", onupdate="CASCADE"),
        primary_key=True,
    )
    size = Column(BigInteger, server_default=text("'0'"))
    extension = Column(VARCHAR(10), nullable=False)
    preview_url = Column(VARCHAR(2083), nullable=False)
    download_url = Column(VARCHAR(2083), nullable=False)
    width = Column(Integer, server_default=text("'0'"))
    height = Column(Integer, server_default=text("'0'"))


class Link(Asset):
    __tablename__ = "links"

    id = Column(
        ForeignKey("assets.id", ondelete="CASCADE", onupdate="CASCADE"),
        primary_key=True,
    )
    url = Column(VARCHAR(2083), nullable=False, comment="The URL of the link")


class Video(Asset):
    __tablename__ = "videos"

    id = Column(
        ForeignKey("assets.id", ondelete="CASCADE", onupdate="CASCADE"),
        primary_key=True,
    )
    size = Column(BigInteger, server_default=text("'0'"))
    extension = Column(VARCHAR(10), nullable=False)
    preview_url = Column(VARCHAR(2083), nullable=False)
    download_url = Column(VARCHAR(2083), nullable=False)
    width = Column(Integer, server_default=text("'0'"))
    height = Column(Integer, server_default=text("'0'"))
    duration = Column(Float(asdecimal=True), server_default=text("'0'"))


class FeatureGroup(Base):
    __tablename__ = "feature_groups"

    id = Column(Integer, primary_key=True)
    name = Column(VARCHAR(255), nullable=False)
    client_id = Column(Integer, nullable=False)
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime, nullable=True)
    deleted_by = Column(Integer, nullable=True)


class Feature(Base):
    __tablename__ = "features"

    id = Column(Integer, primary_key=True)
    name = Column(VARCHAR(255), nullable=False)
    slug = Column(VARCHAR(255), nullable=False)
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime, nullable=True)
    deleted_by = Column(Integer, nullable=True)


class Folder(Base):
    __tablename__ = "folders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(VARCHAR(255), nullable=False)
    parent_id = Column(
        ForeignKey("folders.id", ondelete="CASCADE", onupdate="CASCADE"),
        index=True,
        comment="Null parent means it is a root folder",
    )
    created_by = Column(
        Integer, nullable=False, comment="A reference to the ID of the user"
    )
    icon = Column(VARCHAR(255), nullable=False)
    client_id = Column(Integer, nullable=False)
    is_public = Column(TINYINT, nullable=False, server_default=text("'0'"))
    is_user_folder = Column(TINYINT, nullable=False, server_default=text("'0'"))
    owned_by = Column(
        Integer, nullable=False, comment="A reference to the ID of the user"
    )
    is_deleted = Column(TINYINT, nullable=False, server_default=text("'0'"))
    deleted_at = Column(DateTime, comment="Date and time the folder was deleted")
    deleted_by = Column(
        Integer, nullable=True, comment="A reference to the ID of the user"
    )

    parent = relationship("Folder", remote_side=[id], backref="subfolders")


class Language(Base):
    __tablename__ = "languages"

    id = Column(Integer, primary_key=True)
    name = Column(VARCHAR(255), nullable=False)
    native_name = Column(String(255))
    code_2 = Column(String(2), nullable=False)
    code_3 = Column(String(3), nullable=False)
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime, nullable=True)
    deleted_by = Column(Integer, nullable=False)


class Market(Base):
    __tablename__ = "markets"

    id = Column(Integer, primary_key=True)
    name = Column(VARCHAR(255), nullable=False)
    client_id = Column(Integer, nullable=False)
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime, nullable=True)
    deleted_by = Column(Integer, nullable=False)


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True)
    name = Column(VARCHAR(255), nullable=False)
    slug = Column(VARCHAR(255), nullable=False)
    client_id = Column(Integer, nullable=False)
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime, nullable=True)
    deleted_by = Column(Integer, nullable=False)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(VARCHAR(255), nullable=False)
    client_id = Column(Integer)
    username = Column(VARCHAR(255), nullable=False)
    email = Column(VARCHAR(255), nullable=False)
    market_id = Column(Integer)
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime, nullable=True)
    deleted_by = Column(Integer, nullable=True)


class AssetsFolder(Base):
    __tablename__ = "folders_assets"

    id = Column(Integer, primary_key=True)
    asset_id = Column(
        ForeignKey("assets.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )
    folder_id = Column(
        ForeignKey("folders.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )

    asset = relationship("Asset")
    folder = relationship("Folder")


class AssetsLanguage(Base):
    __tablename__ = "assets_languages"

    id = Column(Integer, primary_key=True)
    asset_id = Column(
        ForeignKey("assets.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )
    language_id = Column(
        ForeignKey("languages.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )

    asset = relationship("Asset")
    language = relationship("Language")


class AssetsTag(Base):
    __tablename__ = "assets_tags"

    id = Column(Integer, primary_key=True)
    asset_id = Column(
        ForeignKey("assets.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )
    tag_id = Column(
        ForeignKey("tags.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )

    asset = relationship("Asset")
    tag = relationship("Tag")


class FeatureGroupsFeatureGroup(Base):
    __tablename__ = "feature_groups_feature_groups"

    id = Column(Integer, primary_key=True)
    parent_feature_group_id = Column(
        ForeignKey("feature_groups.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )
    child_feature_group_id = Column(
        ForeignKey("feature_groups.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )

    child_feature_group = relationship(
        "FeatureGroup",
        primaryjoin="FeatureGroupsFeatureGroup.child_feature_group_id == FeatureGroup.id",
    )
    parent_feature_group = relationship(
        "FeatureGroup",
        primaryjoin="FeatureGroupsFeatureGroup.parent_feature_group_id == FeatureGroup.id",
    )


class FeatureGroupsFeature(Base):
    __tablename__ = "feature_groups_features"

    id = Column(Integer, primary_key=True)
    feature_group_id = Column(
        ForeignKey("feature_groups.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )
    feature_id = Column(
        ForeignKey("features.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )

    feature_group = relationship("FeatureGroup")
    feature = relationship("Feature")


class FeatureGroupsFolder(Base):
    __tablename__ = "feature_groups_folders"

    id = Column(Integer, primary_key=True)
    feature_group_id = Column(
        ForeignKey("feature_groups.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )
    folder_id = Column(
        ForeignKey("folders.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )

    feature_group = relationship("FeatureGroup")
    folder = relationship("Folder")


class FeatureGroupsUser(Base):
    __tablename__ = "feature_groups_users"

    id = Column(Integer, primary_key=True)
    feature_group_id = Column(
        ForeignKey("feature_groups.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id = Column(
        ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )

    feature_group = relationship("FeatureGroup")
    user = relationship("User")


class FoldersMarket(Base):
    __tablename__ = "folders_markets"

    id = Column(Integer, primary_key=True)
    folder_id = Column(
        ForeignKey("folders.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )
    market_id = Column(
        ForeignKey("markets.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )

    folder = relationship("Folder")
    market = relationship("Market")


class UsersFolder(Base):
    __tablename__ = "users_folders"

    id = Column(Integer, primary_key=True)
    user_id = Column(
        ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"), index=True
    )
    folder_id = Column(
        ForeignKey("folders.id", ondelete="CASCADE", onupdate="CASCADE"), index=True
    )
    role = Column(
        ENUM("read", "write", "admin", "owner"),
        nullable=False,
        server_default=text("'read'"),
    )

    folder = relationship("Folder")
    user = relationship("User")
